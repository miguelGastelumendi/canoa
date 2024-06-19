
"""
    Database operations helper
    old `dbQuery.py` file

    mgd
    Equipe da Canoa -- 2024
"""
#cSpell:ignore


def persist_record(db, record: any, task_code: int = 1):
    """
        Args:
          db:  SQLAlchemy()
          record: query
          task_code: int
    """
    try:
        db.session.add(record)
        task_code+= 1
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        e.task_code = task_code
        raise RuntimeError(e)


# eof
