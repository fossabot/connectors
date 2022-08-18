import logging
import math
from typing import Collection, Dict, List, Optional, Tuple

from pydantic import parse_raw_as

from metaphor.common.entity_id import dataset_fullname, to_dataset_entity_id
from metaphor.common.event_util import ENTITY_TYPES
from metaphor.common.extractor import BaseExtractor
from metaphor.common.filter import DatabaseFilter
from metaphor.common.logger import get_logger
from metaphor.common.utils import start_of_day, unique_list
from metaphor.models.crawler_run_metadata import Platform
from metaphor.models.metadata_change_event import (
    DataPlatform,
    Dataset,
    DatasetLogicalID,
    DatasetUpstream,
)
from metaphor.snowflake.accessed_object import AccessedObject
from metaphor.snowflake.auth import connect
from metaphor.snowflake.lineage.config import SnowflakeLineageRunConfig
from metaphor.snowflake.utils import QueryWithParam, async_execute

logger = get_logger(__name__)

# disable logging from sql_metadata
logging.getLogger("Parser").setLevel(logging.CRITICAL)


DEFAULT_EXCLUDED_DATABASES: DatabaseFilter = {"SNOWFLAKE": None}


SUPPORTED_OBJECT_DOMAIN_TYPES = (
    "TABLE",
    "VIEW",
    "MATERIALIZED VIEW",
)


class SnowflakeLineageExtractor(BaseExtractor):
    """Snowflake lineage extractor"""

    def platform(self) -> Optional[Platform]:
        return Platform.SNOWFLAKE

    def description(self) -> str:
        return "Snowflake data lineage crawler"

    @staticmethod
    def config_class():
        return SnowflakeLineageRunConfig

    def __init__(self):
        self.account = None
        self.filter = None
        self.max_concurrency = None
        self.batch_size = None
        self._datasets: Dict[str, Dataset] = {}

    async def extract(
        self, config: SnowflakeLineageRunConfig
    ) -> Collection[ENTITY_TYPES]:
        assert isinstance(config, SnowflakeLineageExtractor.config_class())

        logger.info("Fetching lineage info from Snowflake")

        self.account = config.account
        self.max_concurrency = config.max_concurrency
        self.batch_size = config.batch_size

        self.filter = config.filter.normalize()

        self.filter.excludes = (
            DEFAULT_EXCLUDED_DATABASES
            if self.filter.excludes is None
            else {**self.filter.excludes, **DEFAULT_EXCLUDED_DATABASES}
        )

        start_date = start_of_day(config.lookback_days)

        conn = connect(config)

        with conn:
            cursor = conn.cursor()

            if config.enable_lineage_from_history:
                logger.info("Fetching access and query history")
                # Join QUERY_HISTORY & ACCESS_HISTORY to include only queries that succeeded.
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM
                        SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q,
                        SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY a
                    WHERE q.QUERY_ID = a.QUERY_ID
                        AND q.EXECUTION_STATUS = 'SUCCESS'
                        AND ARRAY_SIZE(a.BASE_OBJECTS_ACCESSED) > 0
                        AND ARRAY_SIZE(a.OBJECTS_MODIFIED) > 0
                        AND a.QUERY_START_TIME > %s
                    ORDER BY a.QUERY_START_TIME ASC
                    """,
                    (start_date,),
                )
                count = cursor.fetchone()[0]
                batches = math.ceil(count / self.batch_size)
                logger.info(f"Total {count} queries, dividing into {batches} batches")

                queries = {
                    x: QueryWithParam(
                        f"""
                        SELECT a.BASE_OBJECTS_ACCESSED, a.OBJECTS_MODIFIED, q.QUERY_TEXT
                        FROM
                            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q,
                            SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY a
                        WHERE q.QUERY_ID = a.QUERY_ID
                            AND q.EXECUTION_STATUS = 'SUCCESS'
                            AND ARRAY_SIZE(a.BASE_OBJECTS_ACCESSED) > 0
                            AND ARRAY_SIZE(a.OBJECTS_MODIFIED) > 0
                            AND a.QUERY_START_TIME > %s
                        ORDER BY a.QUERY_START_TIME ASC
                        LIMIT {self.batch_size} OFFSET %s
                        """,
                        (
                            start_date,
                            x * self.batch_size,
                        ),
                    )
                    for x in range(batches)
                }
                async_execute(
                    conn,
                    queries,
                    "fetch_access_logs",
                    self.max_concurrency,
                    self._parse_access_logs,
                )

            if config.enable_view_lineage:
                logger.info("Fetching direct object dependencies")
                cursor.execute(
                    """
                    SELECT REFERENCED_DATABASE, REFERENCED_SCHEMA, REFERENCED_OBJECT_NAME, REFERENCED_OBJECT_DOMAIN,
                        REFERENCING_DATABASE, REFERENCING_SCHEMA, REFERENCING_OBJECT_NAME, REFERENCING_OBJECT_DOMAIN
                    FROM SNOWFLAKE.ACCOUNT_USAGE.OBJECT_DEPENDENCIES;
                    """
                )
                dependencies = cursor.fetchall()
                self._parse_object_dependencies(dependencies)

        return self._datasets.values()

    def _parse_access_logs(self, batch_number: str, access_logs: List[Tuple]) -> None:
        logger.info(f"access logs batch #{batch_number}")
        for base_objects_accessed, objects_modified, query in access_logs:
            try:
                self._parse_access_log(base_objects_accessed, objects_modified, query)
            except Exception:
                logger.exception(
                    "Failed to parse access log.\n"
                    f"BASE_OBJECTS_ACCESSED: {base_objects_accessed}\n"
                    f"OBJECTS_MODIFIED: {objects_modified}"
                )

    def _parse_access_log(
        self, objects_accessed: str, objects_modified: str, query: str
    ) -> None:
        source_datasets = []

        # Extract source tables/views
        source_objects = parse_raw_as(List[AccessedObject], objects_accessed)
        for obj in source_objects:
            if (
                not obj.objectDomain
                or obj.objectDomain.upper() not in SUPPORTED_OBJECT_DOMAIN_TYPES
            ):
                continue

            full_name = obj.objectName.lower().replace('"', "")
            entity_id = to_dataset_entity_id(
                full_name, DataPlatform.SNOWFLAKE, self.account
            )
            source_datasets.append(str(entity_id))

        source_datasets = unique_list(source_datasets)
        if len(source_datasets) == 0:
            return

        # Assign source tables as upstream of each destination tables
        target_objects = parse_raw_as(List[AccessedObject], objects_modified)
        for obj in target_objects:
            if (
                not obj.objectDomain
                or obj.objectDomain.upper() not in SUPPORTED_OBJECT_DOMAIN_TYPES
            ):
                continue

            parts = obj.objectName.split(".")
            if len(parts) != 3:
                logger.warning(f"Ignore invalid object name: {obj.objectName}")
                continue

            database, schema, name = parts
            full_name = dataset_fullname(database, schema, name)
            if not self.filter.include_table(database, schema, name):
                logger.info(f"Excluding table {full_name}")
                continue

            logical_id = DatasetLogicalID(
                name=full_name, account=self.account, platform=DataPlatform.SNOWFLAKE
            )

            upstream = DatasetUpstream(
                source_datasets=source_datasets, transformation=query
            )

            self._datasets[full_name] = Dataset(
                logical_id=logical_id, upstream=upstream
            )

    def _parse_object_dependencies(self, object_dependencies: List[Tuple]) -> None:
        for (
            source_db,
            source_schema,
            source_table,
            source_object_domain,
            target_db,
            target_schema,
            target_table,
            target_object_domain,
        ) in object_dependencies:
            if (
                not source_object_domain
                or source_object_domain.upper() not in SUPPORTED_OBJECT_DOMAIN_TYPES
                or not target_object_domain
                or target_object_domain.upper() not in SUPPORTED_OBJECT_DOMAIN_TYPES
            ):
                continue

            source_fullname = dataset_fullname(source_db, source_schema, source_table)
            source_entity_id_str = str(
                to_dataset_entity_id(
                    source_fullname, DataPlatform.SNOWFLAKE, self.account
                )
            )

            target_fullname = dataset_fullname(target_db, target_schema, target_table)

            if not self.filter.include_table(target_db, target_schema, target_table):
                logger.info(f"Excluding table {target_fullname}")
                continue

            target_logical_id = DatasetLogicalID(
                name=target_fullname,
                account=self.account,
                platform=DataPlatform.SNOWFLAKE,
            )

            if target_fullname in self._datasets:
                self._datasets[target_fullname].upstream.source_datasets.append(
                    source_entity_id_str
                )
            else:
                self._datasets[target_fullname] = Dataset(
                    logical_id=target_logical_id,
                    upstream=DatasetUpstream(source_datasets=[source_entity_id_str]),
                )
