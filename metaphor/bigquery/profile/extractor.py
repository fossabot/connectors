from concurrent.futures import ThreadPoolExecutor
from functools import partial
from time import sleep
from typing import Collection, List, Optional, Set, Union

try:
    import google.cloud.bigquery as bigquery
    from google.cloud.bigquery import QueryJob, TableReference
except ImportError:
    print("Please install metaphor[bigquery] extra\n")
    raise

from metaphor.bigquery.extractor import BigQueryExtractor, build_client
from metaphor.bigquery.profile.config import BigQueryProfileRunConfig, SamplingConfig
from metaphor.common.column_statistics import ColumnStatistics
from metaphor.common.event_util import ENTITY_TYPES
from metaphor.common.extractor import BaseExtractor
from metaphor.common.filter import DatasetFilter
from metaphor.common.logger import get_logger
from metaphor.models.crawler_run_metadata import Platform
from metaphor.models.metadata_change_event import (
    DataPlatform,
    Dataset,
    DatasetFieldStatistics,
    DatasetLogicalID,
    DatasetSchema,
    EntityType,
    FieldStatistics,
)

logger = get_logger(__name__)


class BigQueryProfileExtractor(BaseExtractor):
    """BigQuery data profile extractor"""

    def platform(self) -> Optional[Platform]:
        return Platform.BIGQUERY

    def description(self) -> str:
        return "BigQuery data profile crawler"

    @staticmethod
    def config_class():
        return BigQueryProfileRunConfig

    def __init__(self):
        self._job_project_id = None
        self._sampling = None
        self._column_statistics = None

    async def extract(
        self, config: BigQueryProfileRunConfig
    ) -> Collection[ENTITY_TYPES]:
        assert isinstance(config, BigQueryProfileExtractor.config_class())

        logger.info("Fetching usage info from BigQuery")

        self._job_project_id = config.job_project_id
        self._sampling = config.sampling
        self._column_statistics = config.column_statistics

        client = build_client(config)
        tables = self._fetch_tables(client, config)
        return self.profile(client, tables, config)

    @staticmethod
    def _fetch_tables(
        client: bigquery.Client, config: BigQueryProfileRunConfig
    ) -> List[TableReference]:

        filter = DatasetFilter.normalize(config.filter)
        tables = []
        for bq_dataset in client.list_datasets():
            dataset_ref = bigquery.DatasetReference(
                client.project, bq_dataset.dataset_id
            )

            logger.info(f"Found dataset {dataset_ref}")

            for bq_table in client.list_tables(bq_dataset.dataset_id):

                table_ref = dataset_ref.table(bq_table.table_id)
                if not filter.include_table(
                    database=table_ref.project,
                    schema=table_ref.dataset_id,
                    table=table_ref.table_id,
                ):
                    logger.info(f"Ignore {table_ref} due to filter config")
                    continue
                logger.info(f"Found table {table_ref}")

                tables.append(table_ref)
        return tables

    def profile(
        self,
        client: bigquery.Client,
        tables: List[TableReference],
        config: BigQueryProfileRunConfig,
    ) -> List[Dataset]:
        jobs: Set[QueryJob] = set()

        def profile(table: TableReference):
            return self._profile_table(client, table, jobs)

        with ThreadPoolExecutor(max_workers=config.max_concurrency) as executor:
            datasets = [dataset for dataset in executor.map(profile, tables)]

        counter = 0
        while jobs:
            finished = len(datasets) - len(jobs)
            if counter % 10 == 0:
                logger.info(
                    f"{finished} jobs done, waiting for {len(jobs)} jobs to finish ..."
                )
            counter += 1
            sleep(1)

        return datasets

    def _profile_table(
        self,
        client: bigquery.Client,
        table: TableReference,
        jobs: Set[QueryJob],
    ) -> Dataset:
        def job_callback(job: QueryJob, schema: DatasetSchema, dataset: Dataset):
            exception = job.exception()
            if exception:
                logger.error(f"Skip {table}, Google Client error: {exception}")
            # The profiling result should only have one row
            elif job.result().total_rows != 1:
                logger.warning(
                    f"Skip {table}, the profiling result has more than one row"
                )
            else:
                try:
                    results = [res for res in next(job.result())]
                    BigQueryProfileExtractor._parse_result(
                        results, schema, dataset, self._column_statistics
                    )
                except AssertionError as error:
                    logger.error(f"Assertion failed during process results, {error}")
                except StopIteration as error:
                    logger.error(f"Invalid result, {error}")
                except (IndexError, ValueError, TypeError) as error:
                    logger.error(f"Unknown error during process results, {error}")
                except BaseException as error:
                    jobs.remove(job.job_id)
                    raise error

            # Always remove job from the set, because the job(future) is fulfill
            jobs.remove(job.job_id)

        dataset = BigQueryProfileExtractor._init_dataset(
            f"{table.project}.{table.dataset_id}.{table.table_id}"
        )
        bq_table = client.get_table(table)
        row_count = bq_table.num_rows
        schema = BigQueryExtractor.parse_schema(bq_table)

        logger.debug(f"building query for {table}")
        sql = self._build_profiling_query(
            schema, table, row_count, self._column_statistics, self._sampling
        )
        job = client.query(sql, project=self._job_project_id)

        jobs.add(job.job_id)
        job.add_done_callback(partial(job_callback, schema=schema, dataset=dataset))
        logger.info(f"Job dispatched for {table}")
        return dataset

    @staticmethod
    def _build_profiling_query(
        schema: DatasetSchema,
        table_ref: TableReference,
        row_count: Union[int, None],
        column_statistics: ColumnStatistics,
        sampling: SamplingConfig,
    ) -> str:
        query = ["SELECT COUNT(1)"]

        for field in schema.fields:
            column = field.field_path
            data_type = field.native_type

            if (
                column_statistics.unique_count
                and not BigQueryProfileExtractor._is_complex(data_type)
            ):
                query.append(f", COUNT(DISTINCT `{column}`)")

            if column_statistics.null_count:
                query.append(f", COUNTIF(`{column}` is NULL)")

            if BigQueryProfileExtractor._is_numeric(data_type):
                if column_statistics.min_value:
                    query.append(f", MIN(`{column}`)")
                if column_statistics.max_value:
                    query.append(f", MAX(`{column}`)")
                if column_statistics.avg_value:
                    query.append(f", AVG(`{column}`)")
                if column_statistics.std_dev:
                    query.append(f", STDDEV(`{column}`)")

        query.append(f" FROM `{table_ref}`")

        if row_count and sampling.percentage < 100 and row_count >= sampling.threshold:
            logger.info(f"Enable table sampling for table: {table_ref}")
            query.append(f" TABLESAMPLE SYSTEM ({int(sampling.percentage)} PERCENT)")

        logger.debug(query)
        return "".join(query)

    @staticmethod
    def _parse_result(
        results: List,
        schema: DatasetSchema,
        dataset: Dataset,
        column_statistics: ColumnStatistics,
    ):
        assert (
            dataset.field_statistics is not None
            and dataset.field_statistics.field_statistics is not None
        )
        fields = dataset.field_statistics.field_statistics

        assert len(results) > 0, f"Empty result for ${dataset.logical_id}"
        row_count = int(results[0])

        index = 1
        for field in schema.fields:
            column = field.field_path
            data_type = field.native_type

            unique_count = None
            if (
                column_statistics.unique_count
                and not BigQueryProfileExtractor._is_complex(data_type)
            ):
                unique_count = float(results[index])
                index += 1

            nulls, non_nulls = None, None
            if column_statistics.null_count:
                nulls = float(results[index])
                non_nulls = row_count - nulls
                index += 1

            min_value, max_value, avg, std_dev = None, None, None, None
            if BigQueryProfileExtractor._is_numeric(data_type):
                if column_statistics.min_value:
                    min_value = (
                        None if results[index] is None else float(results[index])
                    )
                    index += 1

                if column_statistics.max_value:
                    max_value = (
                        None if results[index] is None else float(results[index])
                    )
                    index += 1

                if column_statistics.avg_value:
                    avg = None if results[index] is None else float(results[index])
                    index += 1

                if column_statistics.std_dev:
                    std_dev = None if results[index] is None else float(results[index])
                    index += 1

            fields.append(
                FieldStatistics(
                    field_path=column,
                    distinct_value_count=unique_count,
                    null_value_count=nulls,
                    nonnull_value_count=non_nulls,
                    min_value=min_value,
                    max_value=max_value,
                    average=avg,
                    std_dev=std_dev,
                )
            )

        # Verify that we've consumed all the elements from results
        assert index == len(
            results
        ), f"Unconsumed elements from results for {dataset.logical_id}"

    # See https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#numeric_types
    @staticmethod
    def _is_numeric(data_type: str) -> bool:
        numeric_types = [
            "INTEGER",
            "NUMERIC",
            "INT",
            "SMALLINT",
            "INTEGER",
            "BIGINT",
            "TINYINT",
            "BYTEINT",
            "DECIMAL",
            "BIGNUMERIC",
            "BIGDECIMAL",
            "FLOAT64",
        ]
        return data_type in numeric_types

    @staticmethod
    def _is_complex(data_type: str) -> bool:
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#groupable_data_types
        return data_type in ("RECORD", "JSON", "GEOGRAPHY") or data_type.startswith(
            "ARRAY"
        )

    @staticmethod
    def _init_dataset(full_name: str) -> Dataset:
        dataset = Dataset()
        dataset.entity_type = EntityType.DATASET
        dataset.logical_id = DatasetLogicalID(
            name=full_name, platform=DataPlatform.BIGQUERY
        )

        dataset.field_statistics = DatasetFieldStatistics(field_statistics=[])

        return dataset
