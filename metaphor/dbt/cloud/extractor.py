import json
import shutil
import tempfile
from os import path
from typing import Collection, Dict, Optional, Tuple

import requests

from metaphor.common.base_extractor import BaseExtractor
from metaphor.common.event_util import ENTITY_TYPES
from metaphor.common.logger import get_logger
from metaphor.dbt.cloud.config import DbtCloudConfig
from metaphor.dbt.config import DbtRunConfig
from metaphor.dbt.extractor import DbtExtractor
from metaphor.models.crawler_run_metadata import Platform

logger = get_logger()

ADMIN_API_BASE_URL = "https://cloud.getdbt.com/api/v2"
DBT_DOC_BASE_URL = "https://cloud.getdbt.com/accounts/%d/jobs/%s/docs"


class DbtAdminAPIClient:
    """A client that wraps the dbt Cloud Administrative API

    See https://docs.getdbt.com/dbt-cloud/api-v2 for more details.
    """

    @staticmethod
    def from_config_file(config_file: str) -> "DbtExtractor":
        return DbtExtractor(DbtRunConfig.from_yaml_file(config_file))

    def __init__(self, account_id: int, service_token: str):
        self.account_id = account_id
        self.service_token = service_token

    def _get(self, path: str, params: Optional[Dict] = None):
        url = f"{ADMIN_API_BASE_URL}/accounts/{self.account_id}/{path}"
        req = requests.get(
            url,
            params=params,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Token {self.service_token}",
            },
            timeout=600,  # request timeout 600s
        )

        assert req.status_code == 200, f"{url} returned {req.status_code}"
        return req.json()

    def get_last_successful_run(self, job_id: int) -> Tuple[int, int]:
        """Get the project and run IDs of the last successful run for a job"""

        offset = 0
        page_size = 50
        while True:
            # https://docs.getdbt.com/dbt-cloud/api-v2#operation/listRunsForAccount
            resp = self._get(
                "runs/",
                {
                    "job_definition_id": job_id,
                    "order_by": "-id",
                    "limit": page_size,
                    "offset": offset,
                },
            )

            data = resp.get("data")
            assert len(data) > 0, "Unable to find any successful run"

            for run in data:
                if run.get("status") == 10:
                    return run.get("project_id"), run.get("id")

            offset += page_size

    def get_snowflake_account(self, project_id: int) -> Optional[str]:
        """Get the Snowflake account name for a particular project

        Return None if the project doesn't have a Snowflake connection
        """

        # https://docs.getdbt.com/dbt-cloud/api-v2#operation/getProjectById
        resp = self._get(f"projects/{project_id}")
        connection = resp.get("data").get("connection", {})
        if connection.get("type") != "snowflake":
            return None

        return connection.get("details").get("account")

    def get_run_artifact(self, run_id: int, artifact: str) -> str:
        """Write a particular artifact from a run to a temp file."""

        # https://docs.getdbt.com/dbt-cloud/api-v2#operation/getArtifactsByRunId
        artifact_json = self._get(f"runs/{run_id}/artifacts/{artifact}")

        fd, temp_name = tempfile.mkstemp()
        with open(fd, "w") as fp:
            json.dump(artifact_json, fp)

        pretty_name = f"{path.dirname(temp_name)}/{artifact}"
        shutil.copyfile(temp_name, pretty_name)
        return pretty_name


class DbtCloudExtractor(BaseExtractor):
    """
    dbt cloud metadata extractor
    """

    @staticmethod
    def from_config_file(config_file: str) -> "DbtCloudExtractor":
        return DbtCloudExtractor(DbtCloudConfig.from_yaml_file(config_file))

    def __init__(self, config: DbtCloudConfig):
        super().__init__(config, "dbt cloud metadata crawler", Platform.DBT_MODEL)
        self._account_id = config.account_id
        self._job_id = config.job_id
        self._service_token = config.service_token
        self._meta_ownerships = config.meta_ownerships
        self._meta_tags = config.meta_tags

    async def extract(self) -> Collection[ENTITY_TYPES]:
        logger.info("Fetching metadata from DBT cloud")

        client = DbtAdminAPIClient(self._account_id, self._service_token)

        project_id, run_id = client.get_last_successful_run(self._job_id)
        logger.info(f"Last successful run ID: {run_id}, project ID: {project_id}")

        account = client.get_snowflake_account(project_id)
        if account is not None:
            logger.info(f"Snowflake account: {account}")

        manifest_json = client.get_run_artifact(run_id, "manifest.json")
        logger.info(f"manifest.json saved to {manifest_json}")

        # Pass the path of the downloaded manifest file to the dbt Core extractor
        return await DbtExtractor(
            DbtRunConfig(
                manifest=manifest_json,
                account=account,
                docs_base_url=DBT_DOC_BASE_URL % (self._account_id, self._job_id),
                output=self._output,
                meta_ownerships=self._meta_ownerships,
                meta_tags=self._meta_tags,
            )
        ).extract()
