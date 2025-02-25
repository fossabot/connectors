from unittest.mock import MagicMock, patch

import pytest
import requests

from metaphor.common.base_config import OutputConfig
from metaphor.common.event_util import EventUtil
from metaphor.metabase.config import MetabaseRunConfig
from metaphor.metabase.extractor import MetabaseExtractor
from tests.test_utils import load_json


def dummy_config():
    return MetabaseRunConfig(
        server_url="https://localhost", username="", password="", output=OutputConfig()
    )


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        return


@patch.object(requests, "post")
@patch.object(requests.Session, "get")
@pytest.mark.asyncio
async def test_extractor(
    mock_get_method: MagicMock, mock_post_method: MagicMock, test_root_dir: str
):
    mock_post_method.side_effect = [
        MockResponse({"id": "abc"}),
    ]

    mock_get_method.side_effect = [
        MockResponse(
            load_json(f"{test_root_dir}/metabase/data/databases.json"),
        ),
        MockResponse(
            load_json(f"{test_root_dir}/metabase/data/cards.json"),
        ),
        MockResponse(load_json(f"{test_root_dir}/metabase/data/table86.json")),
        MockResponse(load_json(f"{test_root_dir}/metabase/data/dashboards.json")),
        MockResponse(
            load_json(f"{test_root_dir}/metabase/data/dashboard101.json"),
        ),
    ]

    extractor = MetabaseExtractor(dummy_config())
    events = [EventUtil.trim_event(e) for e in await extractor.extract()]

    assert events == load_json(f"{test_root_dir}/metabase/expected.json")
