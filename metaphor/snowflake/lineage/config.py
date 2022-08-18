from pydantic.dataclasses import dataclass

from metaphor.snowflake.config import SnowflakeRunConfig

DEFAULT_BATCH_SIZE = 100000


@dataclass
class SnowflakeLineageRunConfig(SnowflakeRunConfig):
    # Whether to enable finding view lineage from object dependencies, default True
    enable_view_lineage: bool = True

    # Whether to enable finding table lineage information from access history and query history, default True
    enable_lineage_from_history: bool = True

    # Number of days back in the query log to process
    lookback_days: int = 7

    # The number of access logs fetched in a batch, default to 100000
    batch_size: int = DEFAULT_BATCH_SIZE
