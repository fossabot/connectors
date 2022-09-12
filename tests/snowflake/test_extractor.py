from unittest.mock import patch

from metaphor.common.base_config import OutputConfig
from metaphor.common.filter import DatasetFilter
from metaphor.snowflake.config import SnowflakeRunConfig
from metaphor.snowflake.extractor import SnowflakeExtractor


def test_table_url():
    account = "foo"
    full_name = "this.is.TesT"
    assert (
        SnowflakeExtractor.build_table_url(account, full_name)
        == "https://foo.snowflakecomputing.com/console#/data/tables/detail?databaseName=THIS&schemaName=IS&tableName=TEST"
    )


def test_default_excludes():

    with patch("metaphor.snowflake.auth.connect"):
        extractor = SnowflakeExtractor(
            SnowflakeRunConfig(
                account="snowflake_account",
                user="user",
                password="password",
                filter=DatasetFilter(
                    includes={"foo": None},
                    excludes={"bar": None},
                ),
                output=OutputConfig(),
            )
        )

        assert extractor._filter.includes == {"foo": None}
        assert extractor._filter.excludes == {
            "bar": None,
            "SNOWFLAKE": None,
            "*": {"INFORMATION_SCHEMA": None},
        }
