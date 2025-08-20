"""
DBRecord
--------
Database data retrieve & operations for SQLAlchemy

mgd
Equipe da Canoa --  2024 — 2025
"""

import datetime
import base64
from typing import Optional, List, Any

from ..types_helper import OptListOfStr
from .DBRecord_types import DBRecordData


class DBRecord:
    """
    A class that initializes an instance with attributes from a dictionary.
    """

    # name = "db_record" use  return self.__class__.__name__

    def __init__(
        self,
        record_data: DBRecordData,
        names_filter: OptListOfStr = None,
        types_filter: Optional[List[type]] = None,
    ):
        """
        Args:
            rec_dict (dict): A dictionary containing the attributes to set on the instance.
            names_filter (OptListOfStr): If provided, only sets attributes whose names are in this list
                and return the keys in that order.
            types_filter (Optional[List[type]]): If provided, only sets attributes that match the types in this list.

        Note:
            If `names_filter` is provided, only keys with names in the list will be set as attributes.
            If `types_filter` is provided, only keys with values matching the specified types will be set as attributes.
        """
        if names_filter is None or len(names_filter) == 0:
            key_values = list(record_data.items())
        else:
            key_values: List[tuple[str, Any]] = []
            for field in names_filter:
                if field in record_data:
                    key_values.append((field, record_data[field]))

        for key, value in key_values:
            if isinstance(value, types_filter) if types_filter else True:
                setattr(self, key, value)

    def copy(self, exclude_cols: OptListOfStr = []):
        copy = self.__dict__.copy()
        for ex_col in exclude_cols:
            if ex_col in copy:
                del copy[ex_col]

        return copy

    def encode64(self, exclude_cols: OptListOfStr = []):
        encoded = self.copy(exclude_cols)
        for key, value in encoded.items():
            if isinstance(value, datetime.datetime):
                encoded[key] = value.isoformat()
            elif isinstance(value, str):
                _bytes = value.strip().encode("utf-8")
                encoded[key] = base64.b64encode(_bytes).decode("utf-8")
                # TODO:
                # _b = base64.b64decode(encoded[key])
                # _u = _b.decode("utf-8")
                # if _u != value.strip():
                #     raise Exception(f"Error coding {value}, result {_u}.")

        return encoded

    def keys(self):
        return list(self.__dict__.keys())

    def __getitem__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        raise KeyError(f"'{key}'")

    def __repr__(self):
        attrs = ", ".join(f"{key}={value}" for key, value in self.__dict__.items())
        return f"<{self.__class__.__name__}({attrs})>"


# eof
