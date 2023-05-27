from datetime import datetime, time, timedelta, timezone
from hashlib import md5
from typing import Any, Callable, Dict, List


def start_of_day(daysAgo=0) -> datetime:
    """Returns the start of day in UTC time, for today or N days ago"""
    return datetime.combine(
        datetime.now().date(), time(tzinfo=timezone.utc)
    ) - timedelta(days=daysAgo)


def unique_list(non_unique_list: list) -> list:
    """Returns an order-preserving list with no duplicate elements"""
    return list(dict.fromkeys(non_unique_list))


def filter_empty_strings(original_list: list) -> list:
    return list(filter(lambda e: len(e) > 0, original_list))


def chunks(list, n):
    """Yield successive n-sized chunks from the list."""
    for i in range(0, len(list), n):
        yield list[i : i + n]


def must_set_exactly_one(values: Dict, keys: List[str]):
    not_none = [k for k in keys if values.get(k) is not None]
    if len(not_none) != 1:
        raise ValueError(f"must set exactly one of {keys}, found {not_none}")


def md5_digest(value: bytes) -> str:
    """For computing non-crypto use of MD5 digest"""
    return md5(value).hexdigest()  # nosec B303, B324


def generate_querylog_id(platform: str, id: str) -> str:
    """Generate queryLog id"""
    return f"{platform}:{id}"


def to_utc_time(time: datetime) -> datetime:
    """convert local datatime to utc timezone"""
    return time.replace(tzinfo=timezone.utc)


def chunk_by_size(
    list_to_chunk: list, chunk_size: int, size_func: Callable[[Any], int]
) -> List[slice]:
    """Split a list into the minimum number of chunks smaller than chunk_size

    Normally each chunk is packed with as many successive items as
    possible without exceeding the chunk_size. However, if a single
    item is larger than chunk_size, it'll be put into its own chunk.

    Parameters
    ----------
    list_to_chunk : list
        The list to be chunked
    chunk_size : int
        The ideal size of a chunk
    size_func : Callabale
        A function that computes the size of each item

    Returns
    -------
    list
        a list of slices, each represent a chunk
    """

    start = 0
    slices: List[slice] = []
    slice_size = 0
    for index, item in enumerate(list_to_chunk):
        item_size = size_func(item)
        slice_size += item_size
        if slice_size > chunk_size:
            if start == index:
                # Put an item into its own chunk if it exceeds the chunk size
                slices.append(slice(start, index + 1))
                start = index + 1
                slice_size = 0
            else:
                slices.append(slice(start, index))
                start = index
                slice_size = item_size

    # last chunk
    if slice_size > 0:
        slices.append(slice(start, len(list_to_chunk)))

    return slices
