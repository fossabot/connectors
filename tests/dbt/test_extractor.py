import pytest
from freezegun import freeze_time

from metaphor.common.event_util import EventUtil
from metaphor.dbt.config import DbtRunConfig
from metaphor.dbt.extractor import DbtExtractor
from tests.test_utils import load_json


@pytest.mark.asyncio
async def test_trial_project(test_root_dir):
    await _test_project(
        test_root_dir + "/dbt/data/trial",
        "http://localhost:8080",
        "https://github.com/MetaphorData/dbt/tree/main/trial",
    )


@pytest.mark.asyncio
async def test_ride_share_project(test_root_dir):
    await _test_project(test_root_dir + "/dbt/data/ride_share")


@pytest.mark.asyncio
async def test_shopify_project(test_root_dir):
    await _test_project(test_root_dir + "/dbt/data/shopify")


@freeze_time("2000-01-01")
async def _test_project(data_dir, docs_base_url=None, project_source_url=None):
    manifest = data_dir + "/manifest.json"
    catalog = data_dir + "/catalog.json"
    expected = data_dir + "/results.json"

    config = DbtRunConfig(
        output=None,
        account="metaphor",
        manifest=manifest,
        catalog=catalog,
        docs_base_url=docs_base_url,
        project_source_url=project_source_url,
    )
    extractor = DbtExtractor()
    events = [EventUtil.trim_event(e) for e in await extractor.extract(config)]

    assert events == load_json(expected)
