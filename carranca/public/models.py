"""
    *Users Table*
    Part of Public Access Control Processes

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore nullable sqlalchemy psycopg2 mgmt
from carranca import SqlAlchemySession, login_manager

from typing import Any
from psycopg2 import DatabaseError

from sqlalchemy import select
from sqlalchemy import Column, Computed, Integer, String, DateTime, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin

# from sqlalchemy.orm import Session
# from flask_sqlalchemy import SQLAlchemy

from ..Sidekick import sidekick
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.pw_helper import hash_pass

Base = declarative_base()


class Users(Base, UserMixin):

    __tablename__ = "users"

    # https://docs.sqlalchemy.org/en/13/core/type_basics.html
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True)
    username_lower = Column(String(100), Computed(""))
    email = Column(String(64), unique=True)
    mgmt_sep_id = Column(Integer, unique=True)
    password = Column(LargeBinary)
    last_login_at = Column(DateTime, nullable=True)
    recover_email_token = Column(String(100), nullable=True, unique=True)
    recover_email_token_at = Column(DateTime, Computed(""))
    email_confirmed = Column(Boolean, default=False)
    password_failures = Column(Integer, default=0)
    password_failed_at = Column(DateTime)
    id_role = Column(Integer)
    disabled = Column(Boolean, default=False)

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


## 2023.11.25 @staticmethod
def get_user_where(**filter: Any) -> Users:
    """
    Select a user by a unique filter
    """
    user = None
    with SqlAlchemySession() as db_session:
        stmt = select(Users).filter_by(**filter)
        try:
            user = db_session.execute(stmt).scalar_one_or_none()
        except Exception as e:
            sidekick.app_log.error(f"Error retrieving user {filter}: [{e}].")

    return user


def persist_user(record: any, task_code: int = 1) -> None:
    """
    Updates a user's record
    """
    with SqlAlchemySession() as db_session:
        task_code = 0
        try:
            task_code += 1
            if db_session.object_session(record) is not None:
                sidekick.app_log.debug(f"User record needs an expunge.")
                task_code += 2
                db_session.expunge(record)
            task_code = 3
            db_session.add(record)
            task_code += 1
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            e.task_code = task_code
            raise DatabaseError(e)


# -- Important for user flask manager ---------------------


@login_manager.user_loader
def user_loader(id):
    user = get_user_where(id=id)
    return user


@login_manager.request_loader
def request_loader(request):
    username = "" if len(request.form) == 0 else request.form.get("username")
    user = None if is_str_none_or_empty(username) else get_user_where(username_lower=username.lower())
    return user


# eof
