import json

from metaphor.common.event_util import EventUtil
from metaphor.common.filter import DatasetFilter
from metaphor.snowflake.lineage.extractor import SnowflakeLineageExtractor
from tests.test_utils import load_json


def test_parse_access_log(test_root_dir):
    extractor = SnowflakeLineageExtractor()
    extractor.account = "snowflake_account"
    extractor.filter = DatasetFilter()

    accessed_objects = json.dumps(
        [
            {
                "columns": [
                    {"columnId": 1, "columnName": "FOO"},
                    {"columnId": 2, "columnName": "BAR"},
                ],
                "objectDomain": "Table",
                "objectId": 3,
                "objectName": "DB1.SCHEMA1.TABLE1",
            },
            {
                "columns": [
                    {"columnId": 4, "columnName": "BAZ"},
                    {"columnId": 5, "columnName": "QUX"},
                ],
                "objectDomain": "View",
                "objectId": 6,
                "objectName": "DB1.SCHEMA1.TABLE2",
            },
        ]
    )

    modified_objects = json.dumps(
        [
            {
                "columns": [{"columnId": 7, "columnName": "FOO"}],
                "objectDomain": "TABLE",
                "objectId": 8,
                "objectName": "DB2.SCHEMA1.TABLE1",
            },
            {
                "columns": [{"columnId": 9, "columnName": "BAR"}],
                "objectDomain": "TABLE",
                "objectId": 10,
                "objectName": "DB2.SCHEMA1.TABLE2",
            },
        ]
    )

    extractor._parse_access_log(accessed_objects, modified_objects, "query")

    results = {}
    for key, value in extractor._datasets.items():
        results[key] = EventUtil.clean_nones(value.to_dict())

    assert results == load_json(
        test_root_dir + "/snowflake/lineage/data/parse_query_log_result.json"
    )


def test_parse_object_dependencies(test_root_dir):
    extractor = SnowflakeLineageExtractor()
    extractor.account = "snowflake_account"
    extractor.filter = DatasetFilter()

    dependencies = [
        ("ACME", "METAPHOR", "FOO", "TABLE", "ACME", "METAPHOR", "BAR", "VIEW"),
        ("ACME", "METAPHOR", "ABC", "TABLE", "ACME", "METAPHOR", "XYZ", "VIEW"),
        ("ACME", "METAPHOR", "F", "TABLE", "ACME", "METAPHOR", "B", "STAGE"),
    ]

    extractor._parse_object_dependencies(dependencies)

    results = {}
    for key, value in extractor._datasets.items():
        results[key] = EventUtil.clean_nones(value.to_dict())

    assert results == load_json(
        test_root_dir + "/snowflake/lineage/data/parse_object_dependencies_result.json"
    )
