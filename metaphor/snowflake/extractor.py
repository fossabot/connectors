import math
from datetime import datetime, timezone
from typing import Collection, Dict, List, Mapping, Optional, Tuple

from pydantic import parse_raw_as

from metaphor.common.filter import DatabaseFilter, DatasetFilter
from metaphor.common.query_history import chunk_query_logs
from metaphor.common.utils import md5_digest, start_of_day
from metaphor.snowflake.accessed_object import AccessedObject

try:
    from snowflake.connector.cursor import DictCursor, SnowflakeCursor
    from snowflake.connector.errors import ProgrammingError
except ImportError:
    print("Please install metaphor[snowflake] extra\n")
    raise


from metaphor.common.base_extractor import BaseExtractor
from metaphor.common.entity_id import dataset_fullname
from metaphor.common.event_util import ENTITY_TYPES
from metaphor.common.logger import get_logger
from metaphor.models.crawler_run_metadata import Platform
from metaphor.models.metadata_change_event import (
    DataPlatform,
    Dataset,
    DatasetLogicalID,
    DatasetSchema,
    DatasetStatistics,
    EntityType,
    MaterializationType,
    QueriedDataset,
    QueryLog,
    SchemaField,
    SchemaType,
    SourceInfo,
    SQLSchema,
)
from metaphor.snowflake import auth
from metaphor.snowflake.config import SnowflakeRunConfig
from metaphor.snowflake.utils import (
    DatasetInfo,
    QueryWithParam,
    SnowflakeTableType,
    async_execute,
    exclude_username_clause,
    fetch_query_history_count,
)

logger = get_logger(__name__)

# Filter out "Snowflake" database & all "information_schema" schemas
DEFAULT_FILTER: DatabaseFilter = DatasetFilter(
    excludes={
        "SNOWFLAKE": None,
        "*": {"INFORMATION_SCHEMA": None},
    }
)


class SnowflakeExtractor(BaseExtractor):
    """Snowflake metadata extractor"""

    @staticmethod
    def from_config_file(config_file: str) -> "SnowflakeExtractor":
        return SnowflakeExtractor(SnowflakeRunConfig.from_yaml_file(config_file))

    def __init__(self, config: SnowflakeRunConfig):
        super().__init__(config, "Snowflake metadata crawler", Platform.SNOWFLAKE)
        self._account = config.account
        self._filter = config.filter.normalize().merge(DEFAULT_FILTER)
        self._query_log_excluded_usernames = config.query_log.excluded_usernames
        self._query_log_lookback_days = config.query_log.lookback_days
        self._query_log_fetch_size = config.query_log.fetch_size
        self._max_concurrency = config.max_concurrency

        self._conn = auth.connect(config)
        self._datasets: Dict[str, Dataset] = {}
        self._logs: List[QueryLog] = []

    async def extract(self) -> Collection[ENTITY_TYPES]:

        logger.info("Fetching metadata from Snowflake")

        with self._conn:
            cursor = self._conn.cursor()

            databases = (
                self.fetch_databases(cursor)
                if self._filter.includes is None
                else list(self._filter.includes.keys())
            )
            logger.info(f"Databases to include: {databases}")

            shared_databases = self._fetch_shared_databases(cursor)
            logger.info(f"Shared inbound databases: {shared_databases}")

            for database in databases:
                tables = self._fetch_tables(cursor, database)
                if len(tables) == 0:
                    logger.info(f"Skip empty database {database}")
                    continue

                logger.info(f"Include {len(tables)} tables from {database}")

                self._fetch_columns(cursor, database)
                self._fetch_primary_keys(cursor, database)
                self._fetch_unique_keys(cursor, database)
                self._fetch_table_info(tables, database in shared_databases)

            self._fetch_tags(cursor)

            if self._query_log_lookback_days > 0:
                self._fetch_query_logs()

        entities: List[ENTITY_TYPES] = []
        entities.extend(self._datasets.values())
        entities.extend(chunk_query_logs(self._logs))
        return entities

    @staticmethod
    def fetch_databases(cursor: SnowflakeCursor) -> List[str]:
        cursor.execute(
            "SELECT database_name FROM information_schema.databases ORDER BY database_name"
        )
        return [db[0].lower() for db in cursor]

    @staticmethod
    def _fetch_shared_databases(cursor: SnowflakeCursor) -> List[str]:
        cursor.execute("SHOW SHARES")
        cursor.execute("SELECT * FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))")
        return [db[3].lower() for db in cursor if db[1] == "INBOUND"]

    FETCH_TABLE_QUERY = """
    SELECT table_schema, table_name, table_type, COMMENT, row_count, bytes
    FROM information_schema.tables
    WHERE table_schema != 'INFORMATION_SCHEMA'
    ORDER BY table_schema, table_name
    """

    def _fetch_tables(
        self, cursor: SnowflakeCursor, database: str
    ) -> Dict[str, DatasetInfo]:
        try:
            cursor.execute("USE " + database)
        except ProgrammingError:
            raise ValueError(f"Invalid or inaccessible database {database}")

        cursor.execute(self.FETCH_TABLE_QUERY)

        tables: Dict[str, DatasetInfo] = {}
        for schema, name, table_type, comment, row_count, table_bytes in cursor:
            full_name = dataset_fullname(database, schema, name)
            if not self._filter.include_table(database, schema, name):
                logger.info(f"Ignore {full_name} due to filter config")
                continue

            # TODO: Support dots in database/schema/table name
            if "." in database or "." in schema or "." in name:
                logger.info(
                    f"Ignore {full_name} due to dot in database, schema, or table name"
                )
                continue

            self._datasets[full_name] = self._init_dataset(
                full_name, table_type, comment, row_count, table_bytes
            )
            tables[full_name] = DatasetInfo(database, schema, name, table_type)

        return tables

    def _fetch_columns(self, cursor: SnowflakeCursor, database: str) -> None:
        cursor.execute(
            """
            SELECT table_schema, table_name, column_name, data_type, character_maximum_length,
              numeric_precision, is_nullable, column_default, comment
            FROM information_schema.columns
            WHERE table_schema != 'INFORMATION_SCHEMA'
            ORDER BY table_schema, table_name, ordinal_position
            """
        )

        for (
            table_schema,
            table_name,
            column,
            data_type,
            max_length,
            precision,
            nullable,
            default,
            comment,
        ) in cursor:
            full_name = dataset_fullname(database, table_schema, table_name)
            if full_name not in self._datasets:
                continue

            dataset = self._datasets[full_name]

            assert dataset.schema is not None and dataset.schema.fields is not None

            dataset.schema.fields.append(
                SchemaField(
                    field_path=column,
                    field_name=column,
                    native_type=data_type,
                    max_length=float(max_length) if max_length is not None else None,
                    precision=float(precision) if precision is not None else None,
                    nullable=nullable == "YES",
                    description=comment,
                    subfields=None,
                )
            )

    def _fetch_table_info(self, tables: Dict[str, DatasetInfo], shared: bool) -> None:
        queries, params = [], []
        ddl_tables, updated_time_tables = [], []
        for fullname, table in tables.items():
            # fetch last_update_time and DDL for tables, and fetch only DDL for views
            if table.type == SnowflakeTableType.BASE_TABLE.value:
                queries.append(
                    f'SYSTEM$LAST_CHANGE_COMMIT_TIME(%s) as "UPDATED_{fullname}"'
                )
                params.append(fullname)
                updated_time_tables.append(fullname)

            if not shared:
                queries.append(f"get_ddl('table', %s) as \"DDL_{fullname}\"")
                params.append(fullname)
                ddl_tables.append(fullname)

        if not queries:
            return
        query = f"SELECT {','.join(queries)}"

        cursor = self._conn.cursor(DictCursor)

        try:
            cursor.execute(query, tuple(params))
        except Exception as e:
            logger.exception(f"Failed to execute query:\n{query}\n{e}")
            return

        results = cursor.fetchone()
        assert isinstance(results, Mapping)
        cursor.close()

        for fullname in ddl_tables:
            dataset = self._datasets[fullname]
            assert dataset.schema is not None and dataset.schema.sql_schema is not None

            dataset.schema.sql_schema.table_schema = results[f"DDL_{fullname}"]

        for fullname in updated_time_tables:
            dataset = self._datasets[fullname]
            assert dataset.schema.sql_schema is not None

            # Timestamp is in nanosecond.
            # See https://docs.snowflake.com/en/sql-reference/functions/system_last_change_commit_time.html
            timestamp = results[f"UPDATED_{fullname}"]
            if timestamp > 0:
                dataset.statistics.last_updated = datetime.utcfromtimestamp(
                    timestamp / 1000000000
                ).replace(tzinfo=timezone.utc)

    def _fetch_unique_keys(self, cursor: SnowflakeCursor, database: str) -> None:
        cursor.execute(f"SHOW UNIQUE KEYS IN DATABASE {database}")

        for entry in cursor:
            schema, table_name, column, constraint_name = (
                entry[2],
                entry[3],
                entry[4],
                entry[6],
            )
            table = dataset_fullname(database, schema, table_name)

            dataset = self._datasets.get(table)
            if dataset is None or dataset.schema is None:
                logger.warning(
                    f"Table {table} schema not found for unique key {constraint_name}"
                )
                continue

            field = next(
                (f for f in dataset.schema.fields if f.field_path == column),
                None,
            )
            if not field:
                logger.warning(
                    f"Column {column} not found in table {table} for unique key {constraint_name}"
                )
                continue

            field.is_unique = True

    def _fetch_primary_keys(self, cursor: SnowflakeCursor, database: str) -> None:
        cursor.execute(f"SHOW PRIMARY KEYS IN DATABASE {database}")

        for entry in cursor:
            schema, table_name, column, constraint_name = (
                entry[2],
                entry[3],
                entry[4],
                entry[6],
            )
            table = dataset_fullname(database, schema, table_name)

            dataset = self._datasets.get(table)
            if dataset is None or dataset.schema is None:
                logger.error(
                    f"Table {table} schema not found for primary key {constraint_name}"
                )
                continue

            sql_schema = dataset.schema.sql_schema
            assert sql_schema is not None

            if sql_schema.primary_key is None:
                sql_schema.primary_key = []
            sql_schema.primary_key.append(column)

    def _fetch_tags(self, cursor: SnowflakeCursor) -> None:
        cursor.execute(
            """
            SELECT TAG_NAME, TAG_VALUE, OBJECT_DATABASE, OBJECT_SCHEMA, OBJECT_NAME
            FROM snowflake.account_usage.tag_references
            WHERE domain = 'TABLE'
            ORDER BY OBJECT_DATABASE, OBJECT_SCHEMA, OBJECT_NAME
            """
        )

        for key, value, database, schema, table_name in cursor:
            table = dataset_fullname(database, schema, table_name)

            dataset = self._datasets.get(table)
            if dataset is None or dataset.schema is None:
                logger.error(
                    f"Table {table} not found for tag {self._build_tag_string(key, value)}"
                )
                continue

            if not dataset.schema.tags:
                dataset.schema.tags = []
            dataset.schema.tags.append(self._build_tag_string(key, value))

    def _fetch_query_logs(self) -> None:
        logger.info("Fetching Snowflake query logs")

        start_date = start_of_day(self._query_log_lookback_days)
        end_date = start_of_day()

        count = fetch_query_history_count(
            self._conn, start_date, self._query_log_excluded_usernames, end_date
        )
        batches = math.ceil(count / self._query_log_fetch_size)
        logger.info(f"Total {count} queries, dividing into {batches} batches")

        queries = {
            x: QueryWithParam(
                f"""
                SELECT q.QUERY_ID, q.USER_NAME, QUERY_TEXT, START_TIME, TOTAL_ELAPSED_TIME,
                  BYTES_SCANNED, BYTES_WRITTEN, ROWS_PRODUCED, DIRECT_OBJECTS_ACCESSED, OBJECTS_MODIFIED
                FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q
                JOIN SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY a
                  ON a.QUERY_ID = q.QUERY_ID
                WHERE EXECUTION_STATUS = 'SUCCESS'
                  AND START_TIME > %s AND START_TIME <= %s
                  AND QUERY_START_TIME > %s AND QUERY_START_TIME <= %s
                  {exclude_username_clause(self._query_log_excluded_usernames)}
                ORDER BY q.QUERY_ID
                LIMIT {self._query_log_fetch_size} OFFSET %s
                """,
                (
                    start_date,
                    end_date,
                    start_date,
                    end_date,
                    *self._query_log_excluded_usernames,
                    x * self._query_log_fetch_size,
                ),
            )
            for x in range(batches)
        }
        async_execute(
            self._conn,
            queries,
            "fetch_query_logs",
            self._max_concurrency,
            self._parse_access_logs,
        )

        logger.info(f"Fetched {len(self._logs)} query logs")

    def _parse_access_logs(self, batch_number: str, access_logs: List[Tuple]) -> None:
        logger.info(f"access logs batch #{batch_number}")
        for (
            query_id,
            username,
            query_text,
            start_time,
            elapsed_time,
            bytes_scanned,
            bytes_written,
            rows_produced,
            accessed_objects,
            modified_objects,
        ) in access_logs:
            try:
                sources = self._parse_accessed_objects(accessed_objects)
                targets = self._parse_accessed_objects(modified_objects)

                query_log = QueryLog(
                    id=f"{str(DataPlatform.SNOWFLAKE)}:{query_id}",
                    query_id=query_id,
                    platform=DataPlatform.SNOWFLAKE,
                    start_time=start_time,
                    duration=float(elapsed_time / 1000.0),
                    user_id=username,
                    rows_written=float(rows_produced) if rows_produced else None,
                    bytes_read=float(bytes_scanned) if bytes_scanned else None,
                    bytes_written=float(bytes_written) if bytes_written else None,
                    sources=sources,
                    targets=targets,
                    sql=query_text,
                    sql_hash=md5_digest(query_text.encode("utf-8")),
                )

                self._logs.append(query_log)
            except Exception:
                logger.exception(f"access log processing error, query id: {query_id}")

    @staticmethod
    def _build_tag_string(tag_key: str, tag_value: str) -> str:
        return f"{tag_key}={tag_value}"

    def _init_dataset(
        self,
        full_name: str,
        table_type: str,
        comment: str,
        row_count: Optional[int],
        table_bytes: Optional[float],
    ) -> Dataset:
        dataset = Dataset()
        dataset.entity_type = EntityType.DATASET
        dataset.logical_id = DatasetLogicalID(
            name=full_name, account=self._account, platform=DataPlatform.SNOWFLAKE
        )

        dataset.source_info = SourceInfo(
            main_url=SnowflakeExtractor.build_table_url(self._account, full_name)
        )

        dataset.schema = DatasetSchema(
            schema_type=SchemaType.SQL,
            description=comment,
            fields=[],
            sql_schema=SQLSchema(
                materialization=(
                    MaterializationType.VIEW
                    if table_type == SnowflakeTableType.VIEW.value
                    else MaterializationType.TABLE
                )
            ),
        )

        dataset.statistics = DatasetStatistics()
        if row_count:
            dataset.statistics.record_count = float(row_count)
        if table_bytes:
            dataset.statistics.data_size = table_bytes / (1000 * 1000)  # in MB

        return dataset

    @staticmethod
    def build_table_url(account: str, full_name: str) -> str:
        db, schema, table = full_name.upper().split(".")
        return (
            f"https://{account}.snowflakecomputing.com/console#/data/tables/detail?"
            f"databaseName={db}&schemaName={schema}&tableName={table}"
        )

    @staticmethod
    def _parse_accessed_objects(raw_objects: str) -> List[QueriedDataset]:
        objects = parse_raw_as(List[AccessedObject], raw_objects)
        queried_datasets: List[QueriedDataset] = []
        for obj in objects:
            if not obj.objectDomain or obj.objectDomain.upper() not in (
                "TABLE",
                "VIEW",
                "MATERIALIZED VIEW",
            ):
                continue

            table_name = obj.objectName.lower()
            parts = table_name.split(".")
            if len(parts) != 3:
                logger.debug(f"Invalid table name {table_name}, skip")
                continue

            db, schema, table = parts

            queried_datasets.append(
                QueriedDataset(
                    database=db,
                    schema=schema,
                    table=table,
                    columns=[col.columnName for col in obj.columns] or None,
                )
            )

        return queried_datasets
