"""
 Private Models
    vw_schema_grid
    view for the Schema Grid

mgd
Equipe da Canoa -- 2025.07.24
"""

# Equipe da Canoa -- 2024
#
# cSpell:ignore: nullable sqlalchemy sessionmaker sep ssep scm sepsusr usrlist SQLA duovigesimal

from typing import List, Optional
from sqlalchemy import (
    Computed,
    Boolean,
    Column,
    Integer,
    String,
    select,
)
from sqlalchemy.orm import Session

from ...models import SQLABaseTable
from ...helpers.db_helper import db_fetch_rows
from ...private.IdToCode import IdToCode
from ...helpers.db_records.DBRecords import DBRecords


# --- View ---
class SchemaGrid(SQLABaseTable):
    __tablename__ = "vw_schema_grid"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(100))
    color = Column(String(9))
    title = Column(String(140))
    visible = Column(Boolean)
    sep_count = Column(Integer)
    v_sep_count = Column(Integer, Computed(""))  # visible sep
    ui_order = Column(Integer, Computed(""))
    sep_v2t = Column(String(11), Computed(""))  # visible / total

    id_to_code = IdToCode()

    @staticmethod
    def code(id: int) -> str:
        return SchemaGrid.id_to_code.encode(id)

    @staticmethod
    def get_schemas(field_names: Optional[List[str]] = None) -> DBRecords:
        """
        Returns:
          All records from SchemaGrid table, optional of selected fields
        """

        def _get_data(db_session: Session):
            def __cols() -> List[Column]:
                all_cols = SchemaGrid.__table__.columns
                _cols = [col for col in all_cols if col.name in field_names]
                return _cols

            sel_cols = __cols() if field_names else None

            stmt = select(*sel_cols) if sel_cols else select(SchemaGrid)
            rows = db_session.execute(stmt).all()
            recs = DBRecords(stmt, rows)
            return recs

        _, _, scm_recs = db_fetch_rows(_get_data, SchemaGrid.__tablename__)
        return scm_recs


# eof
