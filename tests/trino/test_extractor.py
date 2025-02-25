import time

import pytest
from testcontainers.general import DockerContainer

from metaphor.common.base_config import OutputConfig
from metaphor.common.event_util import EventUtil
from metaphor.common.filter import DatasetFilter
from metaphor.common.logger import get_logger
from metaphor.models.metadata_change_event import Dataset, QueryLogs
from metaphor.trino.config import TrinoRunConfig
from metaphor.trino.extractor import TrinoExtractor
from tests.test_utils import load_json

logger = get_logger()


@pytest.mark.asyncio
async def test_extractor(test_root_dir: str) -> None:
    with DockerContainer("trinodb/trino").with_exposed_ports(8080) as container:
        port = container.get_exposed_port(8080)
        host = container.get_container_host_ip()

        while container.exec("/usr/lib/trino/bin/health-check").exit_code:
            logger.info("Waiting for Trino server to start")
            time.sleep(1)

        dataset_filter = DatasetFilter(
            excludes={
                "jmx": None,
                "memory": None,
                "tpcds": None,
            }
        )
        config = TrinoRunConfig(
            output=OutputConfig(),
            host=host,
            port=int(port),
            filter=dataset_filter,
            username="metaphor-dev",
        )
        entities = await TrinoExtractor(config).extract()

        datasets = [entity for entity in entities if isinstance(entity, Dataset)]
        dataset_events = [EventUtil.trim_event(dataset) for dataset in datasets]
        assert dataset_events == [
            obj
            for obj in load_json(f"{test_root_dir}/trino/expected.json")
            if obj.get("entityType") == "DATASET"
        ]

        query_logs = [entity for entity in entities if isinstance(entity, QueryLogs)]
        extracted_query_logs = [
            EventUtil.trim_event(query_log) for query_log in query_logs
        ][0]["logs"]
        expected_query_logs = [
            obj
            for obj in load_json(f"{test_root_dir}/trino/expected.json")
            if obj.get("logs")
        ][0]["logs"]
        for expected in expected_query_logs:
            extracted = next(
                (
                    log
                    for log in extracted_query_logs
                    if log["sqlHash"] == expected["sqlHash"]
                ),
                None,
            )
            assert extracted
            # Can't compare queryId, duration and start_time, as they are generated by trino on start up.
        assert len(expected_query_logs) == len(extracted_query_logs)
