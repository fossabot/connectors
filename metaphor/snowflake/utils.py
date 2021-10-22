import logging
import time
from concurrent import futures
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from snowflake.connector import SnowflakeConnection
from snowflake.connector.cursor import SnowflakeCursor

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEFAULT_THREAD_POOL_SIZE = 10
DEFAULT_SLEEP_TIME = 0.1  # 0.1 s


@dataclass
class DatasetInfo:
    database: str
    schema: str
    name: str
    type: str


@dataclass
class QueryWithParam:
    query: str
    params: Optional[Tuple] = None


def async_query(conn: SnowflakeConnection, query: QueryWithParam) -> SnowflakeCursor:
    """Executing a snowflake query asynchronously"""
    cursor = conn.cursor()
    if query.params is not None:
        cursor.execute_async(query.query, query.params)
    else:
        cursor.execute_async(query.query)

    query_id = cursor.sfqid

    # Wait for the query to finish running.
    while conn.is_still_running(conn.get_query_status(query_id)):
        time.sleep(DEFAULT_SLEEP_TIME)

    cursor.get_results_from_sfqid(query_id)
    return cursor


def async_execute(
    conn: SnowflakeConnection,
    queries: Dict[str, QueryWithParam],
    query_name: str = "",
    max_workers: Optional[int] = None,
) -> Dict[str, List]:
    """Executing snowflake query with a set of parameters using thread pool"""
    workers = max_workers if max_workers is not None else DEFAULT_THREAD_POOL_SIZE
    with futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_map = {
            executor.submit(async_query, conn, query): key
            for key, query in queries.items()
        }

        results = {}
        for future in futures.as_completed(future_map):
            key = future_map[future]
            try:
                results[key] = future.result().fetchall()
            except Exception as ex:
                logger.error(f"Error executing {query_name} for {key}", ex)

        return results
