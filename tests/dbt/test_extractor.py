import pytest

from metaphor.common.base_config import OutputConfig
from metaphor.common.event_util import EventUtil
from metaphor.dbt.config import DbtRunConfig, MetaOwnership, MetaTag
from metaphor.dbt.extractor import DbtExtractor
from metaphor.dbt.manifest_parser import ManifestParser
from tests.test_utils import load_json


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


@pytest.mark.asyncio
async def test_jaffle_v10(test_root_dir):
    await _test_project(
        test_root_dir + "/dbt/data/jaffle_v10",
        "http://localhost:8080",
        "https://github.com/MetaphorData/dbt/tree/main/jaffle-sl-template",
    )


async def _test_project(
    data_dir, docs_base_url=None, project_source_url=None, useCatalog=False
):
    manifest = data_dir + "/manifest.json"
    expected = data_dir + "/results.json"

    config = DbtRunConfig(
        output=OutputConfig(),
        account="metaphor",
        manifest=manifest,
        docs_base_url=docs_base_url,
        project_source_url=project_source_url,
        meta_ownerships=[MetaOwnership(meta_key="owner", ownership_type="Maintainer")],
        meta_tags=[MetaTag(meta_key="pii", tag_type="PII")],
    )
    extractor = DbtExtractor(config)
    events = [EventUtil.trim_event(e) for e in await extractor.extract()]

    assert events == load_json(expected)


def test_sanitize_manifest_empty_docs(test_root_dir):
    manifest = {
        "docs": {"foo": "bar"},
    }

    assert ManifestParser.sanitize_manifest(manifest, "v10") == {
        "docs": {},
    }


def test_sanitize_manifest_strip_null_tests_depends_on(test_root_dir):
    manifest = {
        "nodes": {
            "test.example": {
                "depends_on": {
                    "macros": [None, "macro1"],
                    "nodes": ["node1", None, "node2"],
                }
            }
        }
    }

    assert ManifestParser.sanitize_manifest(manifest, "v10") == {
        "nodes": {
            "test.example": {
                "depends_on": {
                    "macros": ["macro1"],
                    "nodes": ["node1", "node2"],
                }
            }
        }
    }
