"""
DBRecords
---------
Database data retrieve & operations for SQLAlchemy

mgd
Equipe da Canoa --  2024 — 2025
"""

# cspell:ignore SQLA sqla froms

from typing import Optional, TypeAlias, List, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy import Row

from ..py_helper import class_to_dict

from .DBRecord import DBRecord

ListOfDBRecords: TypeAlias = List["DBRecord"]


class DBRecords:
    """
    A class that converts a SQLAlchemy query result into a list of DBRecord instances.
    """

    from .DBRecord_types import SQLAStatement, SQLABaseRecords

    simple_types_filter: Tuple[type, ...] = (str, int, float, bool, datetime)

    def __init__(
        self,
        sqla_stmt: SQLAStatement,
        sqla_records: Optional[SQLABaseRecords] = None,
        allowed_field_names: Optional[List[str]] = None,
        allowed_field_types: Optional[Tuple[type, ...]] = None,
        includeNone: bool = True,
    ):
        # Find the table Name
        self.records: ListOfDBRecords = []
        if sqla_stmt.is_select:
            froms = sqla_stmt.columns_clause_froms
            self.table_name = froms[0].name if len(froms) == 1 else ",".join([f.name for f in froms])
        elif sqla_stmt.is_table:
            self.table_name = sqla_stmt.name

        # Fields names filter required?
        self.allowed_field_names = (
            allowed_field_names
            if isinstance(allowed_field_names, List) and len(allowed_field_names) > 0
            else None
        )
        # Fields values types were specified?
        self.allowed_field_types = (
            allowed_field_types if allowed_field_types is not None else DBRecords.simple_types_filter
        )

        if includeNone:
            self.allowed_field_types += (type(None),)

        self.records = []
        if sqla_records is None:
            return

        first_record = sqla_records[0]
        if isinstance(first_record, Row):
            # Handle SQLAlchemy Row objects

            # Get dict representation of records
            dict_data = [r._asdict() for r in sqla_records]

            # Handles (maybe) nested view issue (done studying the attributes of same instances, so try/except)
            try:

                def _step_in(table_name: str) -> Dict:
                    return [class_to_dict(item[table_name]) for item in dict_data]

                _key = "plugin_subject"
                if self.table_name in dict_data[0]:
                    dict_data = _step_in(self.table_name)
                elif (tbl_c := sqla_stmt._propagate_attrs[_key].class_.__name__) and tbl_c in dict_data[0]:
                    dict_data = _step_in(tbl_c)
            except:
                pass

            # Create the records from dict_data (rows._asdict())
            self.records = [
                DBRecord(rec, self.allowed_field_names, self.allowed_field_types) for rec in dict_data
            ]

        elif isinstance(first_record, tuple):
            # Handle tuples
            if hasattr(sqla_stmt, "c"):
                column_names = [col.name for col in sqla_stmt.c]
            elif hasattr(sqla_stmt, "selected_columns"):
                column_names = [col.name for col in sqla_stmt.selected_columns]
            else:
                raise ValueError(f"Cannot determine column names for {sqla_stmt}")
            self.records = [
                DBRecord(dict(zip(column_names, row)), self.allowed_field_names, self.allowed_field_types)
                for row in sqla_records
            ]

        else:
            dict_data = [class_to_dict(r) for r in sqla_records]
            self.records = [
                DBRecord(rec, self.allowed_field_names, self.allowed_field_types) for rec in dict_data
            ]

    def __iter__(self):
        """make DBRecords iterable"""
        return iter(self.records)

    def __len__(self):
        """make DBRecords have len"""
        return len(self.records)

    def __getitem__(self, index):
        """make DBRecords subscriptable"""
        return self.records[index]

    @property
    def count(self) -> int:
        return self.__len__()

    def append(self, record_dict: Dict[str, Any]) -> None:
        """Appends a new DBRecord object based on records list."""
        new_record = DBRecord(record_dict, self.allowed_field_names, self.allowed_field_types)
        self.records.append(new_record)

    def to_list(self, exclude_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        exclude_fields = (exclude_fields or []) + ["__class__.__name__"]
        list = [
            {key: value for key, value in record.__dict__.items() if key not in exclude_fields}
            for record in self.records
        ]
        return list

    def keys(self):
        return self.records[0].keys() if len(self.records) > 0 else []

    def __repr__(self):
        attrs = ", ".join(f"{key}={value}" for key, value in self.__dict__.items())
        return f"<{self.table_name}({attrs})>"


# eof
