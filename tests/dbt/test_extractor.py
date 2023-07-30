import pytest

from metaphor.common.base_config import OutputConfig
from metaphor.common.event_util import EventUtil
from metaphor.dbt.config import DbtRunConfig, MetaOwnership, MetaTag
from metaphor.dbt.extractor import DbtExtractor
from tests.test_utils import load_json


@pytest.mark.asyncio
async def test_trial_project_v1(test_root_dir):
    await _test_project(
        test_root_dir + "/dbt/data/trial_v1",
        "http://localhost:8080",
        "https://github.com/MetaphorData/dbt/tree/main/trial",
    )


@pytest.mark.asyncio
async def test_trial_project_v2(test_root_dir):
    await _test_project(
        test_root_dir + "/dbt/data/trial_v2",
        "http://localhost:8080",
        "https://github.com/MetaphorData/dbt/tree/main/trial",
    )


@pytest.mark.asyncio
async def test_trial_project_v3(test_root_dir):
    await _test_project(
        test_root_dir + "/dbt/data/trial_v3",
        "http://localhost:8080",
        "https://github.com/MetaphorData/dbt/tree/main/trial",
    )


@pytest.mark.asyncio
async def test_trial_project_v4(test_root_dir):
    await _test_project(
        test_root_dir + "/dbt/data/trial_v4",
        "http://localhost:8080",
        "https://github.com/MetaphorData/dbt/tree/main/trial",
    )


@pytest.mark.asyncio
async def test_trial_project_v5(test_root_dir):
    await _test_project(
        test_root_dir + "/dbt/data/trial_v5",
        "http://localhost:8080",
        "https://github.com/MetaphorData/dbt/tree/main/trial",
    )


@pytest.mark.asyncio
async def test_trial_project_v6(test_root_dir):
    await _test_project(
        test_root_dir + "/dbt/data/trial_v6",
        "http://localhost:8080",
        "https://github.com/MetaphorData/dbt/tree/main/trial",
    )


@pytest.mark.asyncio
async def test_trial_project_v7(test_root_dir):
    await _test_project(
        test_root_dir + "/dbt/data/trial_v7",
        "http://localhost:8080",
        "https://github.com/MetaphorData/dbt/tree/main/trial",
    )


@pytest.mark.asyncio
async def test_trial_project_v8(test_root_dir):
    await _test_project(
        test_root_dir + "/dbt/data/trial_v8",
        "http://localhost:8080",
        "https://github.com/MetaphorData/dbt/tree/main/trial",
    )


@pytest.mark.asyncio
async def test_trial_project_v9(test_root_dir):
    await _test_project(
        test_root_dir + "/dbt/data/trial_v9",
        "http://localhost:8080",
        "https://github.com/MetaphorData/dbt/tree/main/trial",
    )


async def _test_project(
    data_dir, docs_base_url=None, project_source_url=None, useCatalog=False
):
    manifest = data_dir + "/manifest.json"
    catalog = data_dir + "/catalog.json" if useCatalog else None
    expected = data_dir + "/results.json"

    config = DbtRunConfig(
        output=OutputConfig(),
        snowflake_account="metaphor",
        manifest=manifest,
        catalog=catalog,
        docs_base_url=docs_base_url,
        project_source_url=project_source_url,
        meta_ownerships=[MetaOwnership(meta_key="owner", ownership_type="Maintainer")],
        meta_tags=[MetaTag(meta_key="pii", tag_type="PII")],
    )
    extractor = DbtExtractor(config)
    events = [EventUtil.trim_event(e) for e in await extractor.extract()]

    assert events == load_json(expected)
