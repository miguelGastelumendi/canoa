"""
    Database operations helper
    old `dbQuery.py` file

    mgd
    Equipe da Canoa -- 2024
"""

# cSpell:ignore psycopg2

from psycopg2 import DatabaseError


def persist_record(db, record: any, task_code: int = 1) -> None:
    """
    Args:
      db:  SQLAlchemy()
      record: query result
      task_code: int
    """
    try:
        db.session.add(record)
        task_code += 1
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        e.task_code = task_code
        raise DatabaseError(e)


def get_str_field_length(table_model: object, field_name: str) -> str:
    """
    Args:
      table_model: Flask SQLAlchemy Table Model
      field_name: the field name (must be string)
    Returns:
      the maximum size defined for the column in the Table Model (*not on the DB*)
    """
    fields = table_model.__table__.columns
    return fields[field_name].type.length

# eof
