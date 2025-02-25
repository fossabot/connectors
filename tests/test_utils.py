import json
from datetime import datetime
from typing import Any


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def compare_list_ignore_order(a: list, b: list):
    t = list(b)  # make a mutable copy
    try:
        for elem in a:
            t.remove(elem)
    except ValueError:
        return False
    return not t


def ignore_datetime_values(  # noqa C901
    obj: Any, format: str = "%Y-%m-%dT%H:%M:%S.%f%z"
):
    if isinstance(obj, dict):
        keys_to_remove = []
        for key, value in obj.items():
            if isinstance(value, str):
                try:
                    datetime.strptime(value, format)
                    keys_to_remove.append(key)
                except ValueError:
                    pass
            elif isinstance(value, (list, dict)):
                ignore_datetime_values(value, format)

        for key in keys_to_remove:
            del obj[key]

    elif isinstance(obj, list):
        indices_to_remove = []
        for i, item in enumerate(obj):
            if isinstance(item, str):
                try:
                    datetime.strptime(item, format)
                    indices_to_remove.append(i)
                except ValueError:
                    pass
            elif isinstance(item, (list, dict)):
                ignore_datetime_values(item, format)

        indices_to_remove.reverse()
        for i in indices_to_remove:
            del obj[i]

        # Remove any empty dictionaries from the list
        obj[:] = [item for item in obj if item != {}]

    if isinstance(obj, (list, dict)) and not obj:
        return None  # Remove empty list or dict
    return obj
