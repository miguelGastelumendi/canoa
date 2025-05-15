"""
Data Types
----------
Database data retrieve & operations for SQLAlchemy

mgd
Equipe da Canoa --  2024 — 2025
"""

# cspell:ignore SQLA

from typing import TypeAlias, Dict, List, Any
from datetime import datetime

JsonStrOfRecords: TypeAlias = str

DBRecordData: TypeAlias = Dict[str, str | int | float | bool | datetime]

# see  declarative_base
# https://stackoverflow.com/questions/45259764/how-to-create-a-single-table-using-sqlalchemy-declarative-base
# see ...private.models Base = declarative_base()

SQLABaseTable: TypeAlias = Any  # reduce to types

SQLAStatement: TypeAlias = Any  # reduce to types

SQLABaseRecords: TypeAlias = List[Any]  # improve
# eof
