"""
    Database data retrieve operations helper

    mgd
    Equipe da Canoa -- 2024
"""

# cSpell:ignore psycopg2 sqlalchemy

from typing import Tuple
from psycopg2 import DatabaseError
from sqlalchemy import text

from ..main import shared
from .py_helper import is_str_none_or_empty


def is_connected() -> bool:
    """
    Checks the database connection status.

    Returns:
        True if the connection is successful, False otherwise.
    """

    try:
        shared.db_engine.connect()
        return True
    except Exception as e:
        shared.app_log.error(f"Connection Error: [{e}].")
        return False


def execute_sql(query: str):
    """ Runs an SQL query and returns the result """
    result = None
    if not is_str_none_or_empty(query):
        with shared.db_engine.connect() as connection:
            _text = text(query)
            result = connection.execute(_text)

    return result


def retrieve_data(query: str) -> any | Tuple:
  """
  Executes the given SQL query and returns the result in 3 modes:
    1.  N rows 1 column
    2.  1 row N columns
    3.  1 row 1 column

  Args:
    sql: The SQL query to execute.

  Returns:
    - A tuple of values if the query returns multiple rows with a single column each.
    - A tuple of values if the query returns a single row with multiple columns.
    - A single value if the query returns a single row with a single column.
    - None if an error occurs or the query returns no results.
  """

  try:
    data_rows = execute_sql(query)
    data = data_rows.fetchall()

    if not data:
        return None
    elif len(data) > 1:
        # Multiple rows with a single column each
        return tuple(line[0] for line in data)
    elif len(data[0]) > 1:
        # Single row with multiple columns
        return tuple(data[0])
    else:
        # Single row with a single column
        return data[0][0]
  except Exception as e:
    shared.app_log.error(f"An error occurred retrieving db data [{query}]: {e}")
    return None


def retrieve_dict(query: str):
    data = retrieve_data(query)

    result = {}
    try:
        if data and isinstance(data, tuple):
            result = {row[0]: row[1] for row in data}
    except Exception as e:
        shared.app_log.error(f"An error occurred loading the dict from [{query}]: {e}")

    # # Check if the result is a tuple of tuples (multiple rows)
    # if isinstance(data, tuple) and all(isinstance(row, tuple) and len(row) >= 2 for row in data):
    #     # We expect at least two columns (key, value) for dictionary creation
    #     return {row[0]: row[1] for row in data}

    return result


def persist_record(record: any, task_code: int = 1) -> None:
    """
    Args:
      db:  SQLAlchemy()
      record: query result
      task_code: int
    """
    try:
        shared.db.session.add(record)
        task_code += 1
        shared.db.session.commit()
    except Exception as e:
        shared.db.session.rollback()
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
