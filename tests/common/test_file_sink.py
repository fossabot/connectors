import tempfile

from metaphor.models.metadata_change_event import (
    MetadataChangeEvent,
    Person,
    PersonLogicalID,
)

from metaphor.common.file_sink import FileSink, FileSinkConfig
from tests.test_utils import load_json


def events_from_json(file):
    return [MetadataChangeEvent.from_dict(json) for json in load_json(file)]


def test_file_sink_no_split(test_root_dir):
    output = tempfile.mktemp(suffix=".json")
    prefix = output[0:-5]

    messages = [
        MetadataChangeEvent(person=Person(logical_id=PersonLogicalID("foo1@bar.com"))),
        MetadataChangeEvent(person=Person(logical_id=PersonLogicalID("foo2@bar.com"))),
    ]

    sink = FileSink(FileSinkConfig(path=output, bach_size=2))
    assert sink.sink(messages) is True
    assert messages == events_from_json(f"{prefix}-1-of-1.json")


def test_file_sink_split(test_root_dir):
    output = tempfile.mktemp(suffix=".json")
    prefix = output[0:-5]

    messages = [
        MetadataChangeEvent(person=Person(logical_id=PersonLogicalID("foo1@bar.com"))),
        MetadataChangeEvent(person=Person(logical_id=PersonLogicalID("foo2@bar.com"))),
        MetadataChangeEvent(person=Person(logical_id=PersonLogicalID("foo3@bar.com"))),
        MetadataChangeEvent(person=Person(logical_id=PersonLogicalID("foo4@bar.com"))),
        MetadataChangeEvent(person=Person(logical_id=PersonLogicalID("foo5@bar.com"))),
    ]

    sink = FileSink(FileSinkConfig(path=output, bach_size=2))
    assert sink.sink(messages) is True
    assert messages[0:2] == events_from_json(f"{prefix}-1-of-3.json")
    assert messages[2:4] == events_from_json(f"{prefix}-2-of-3.json")
    assert messages[4:] == events_from_json(f"{prefix}-3-of-3.json")
