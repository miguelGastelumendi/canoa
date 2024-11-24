"""
    *Users Table*
    Part of Public Access Control Processes

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore nullable sqlalchemy psycopg2 mgmt
from carranca import Session, db, login_manager

from typing import Any
from psycopg2 import DatabaseError

# from sqlalchemy import select
from sqlalchemy import Column, Computed, Integer, String, DateTime, Boolean, LargeBinary
from flask_login import UserMixin

# from sqlalchemy.orm import Session
# from flask_sqlalchemy import SQLAlchemy

from ..Sidekick import sidekick
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.pw_helper import hash_pass


class Users(UserMixin, db.Model):

    __tablename__ = "users"

    # https://docs.sqlalchemy.org/en/13/core/type_basics.html
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True)
    username_lower = Column(String(100), Computed(""))  # TODO deferred
    email = Column(String(64), unique=True)
    password = Column(LargeBinary)
    last_login_at = Column(DateTime, nullable=True)
    recover_email_token = Column(String(100), nullable=True)
    recover_email_token_at = Column(DateTime, Computed(""))
    id_role = Column(Integer)
    disabled = Column(Boolean, default=False)
    mgmt_sep_id = Column(Integer)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (tra_vis flake8 test)
                value = value[0]

            if property == "password":
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


@staticmethod
def get_user_where(**kwargs: Any) -> Users:
    """
    Select a user by a unique filter
    This def if to avoid the use of .first, like in:
        `r= Users.query.filter_by(username_lower = username.lower()).first()`
    that can rais an error, see this code.
    """
    user = None
    session = Session()
    try:
        records = session.query(Users).filter_by(**kwargs)
        if not records or records.count() == 0:
            pass
        elif records.count() == 1:
            user = records.first()
        else:
            msg = f"The selection return {records.count()} users, expect one or none."
            sidekick.app_log.error(msg)
            raise KeyError(msg)
    finally:
        session.close()

    return user


def persist_user(record: any, task_code: int = 1) -> None:
    session = Session()
    task_code = 0
    try:
        task_code += 1
        if session.object_session(record) is not None:
            task_code += 2
            session.expunge(record)
        task_code = 3
        session.add(record)
        task_code += 1
        session.commit()
    except Exception as e:
        session.rollback()
        e.task_code = task_code
        raise DatabaseError(e)
    finally:
        session.close()


@login_manager.user_loader
def user_loader(id):
    return Users.query.get(id)


@login_manager.request_loader
def request_loader(request):
    username = "" if len(request.form) == 0 else request.form.get("username")
    user = None if is_str_none_or_empty(username) else get_user_where(username_lower=username.lower())
    return user


# eof
