from unittest.mock import MagicMock, patch

import pytest

from metaphor.common.base_config import OutputConfig
from metaphor.common.event_util import EventUtil
from metaphor.thought_spot.config import ThoughtSpotRunConfig
from metaphor.thought_spot.extractor import ThoughtSpotExtractor
from tests.test_utils import load_json


def dummy_config():
    return ThoughtSpotRunConfig(
        user="user",
        password="password",
        base_url="http://base.url",
        output=OutputConfig(),
    )


@pytest.mark.asyncio
async def test_extractor(test_root_dir):
    def create_mock_client():
        mock = MagicMock()
        mock.metadata = None
        return mock

    with patch(
        "metaphor.thought_spot.utils.ThoughtSpot.create_client"
    ) as mock_create_client, patch(
        "metaphor.thought_spot.utils.ThoughtSpot._fetch_headers"
    ) as mock_fetch_headers, patch(
        "metaphor.thought_spot.utils.ThoughtSpot._fetch_object_detail"
    ) as mock_fetch_object_detail, patch(
        "metaphor.thought_spot.utils.ThoughtSpot._fetch_tml"
    ) as mock_fetch_tml:
        mock_create_client.return_value = create_mock_client()
        mock_fetch_headers.return_value = []
        mock_fetch_object_detail.side_effect = [
            load_json(f"{test_root_dir}/thought_spot/data/connections.json"),
            load_json(f"{test_root_dir}/thought_spot/data/data_objects.json"),
            load_json(f"{test_root_dir}/thought_spot/data/answers.json"),
            load_json(f"{test_root_dir}/thought_spot/data/liveboards.json"),
        ]
        mock_fetch_tml.return_value = load_json(
            f"{test_root_dir}/thought_spot/data/tml.json"
        )

        extractor = ThoughtSpotExtractor(dummy_config())
        events = [EventUtil.trim_event(e) for e in await extractor.extract()]

    assert events == load_json(f"{test_root_dir}/thought_spot/expected.json")
