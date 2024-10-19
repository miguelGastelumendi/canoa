"""
    *Users Table*
    Part of Public Access Control Processes

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore nullable sqlalchemy psycopg2

from typing import Any
from psycopg2 import DatabaseError
from sqlalchemy import select
from sqlalchemy import Column, Computed, Integer, String, DateTime, Boolean, LargeBinary
from flask_login import UserMixin
from sqlalchemy.orm import Session
from flask_sqlalchemy import SQLAlchemy

from ..main import shared
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.pw_helper import hash_pass


class Users(UserMixin, shared.db().Model):

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


def get_user_where(**kwargs: Any) -> Any:
    """
    Select a user by a unique filter
    This def if to avoid the use of .first, like in:
        `r= Users.query.filter_by(username_lower = username.lower()).first()`
    that can rais an error, see this code.
    """
    user = None
    records = Users.query.filter_by(**kwargs)
    if not records or records.count() == 0:
        pass
    elif records.count() == 1:
        user = records.first()
    else:
        msg = f"The selection return {records.count()} users, expect one or none."
        shared.app_log.error(msg)
        raise KeyError(msg)

    return user

def persist_user(record: any, task_code: int = 1) -> None:
    # as this model inherits from SQLAlchemy (sa) the session must be from sa
    sa = shared.db()
    try:
        sa.session.add(record)
        task_code += 1
        sa.session.commit()
    except Exception as e:
        sa.session.rollback()
        e.task_code = task_code
        raise DatabaseError(e)


@shared.login_manager.user_loader
def user_loader(id):
    return Users.query.get(id)
    # mgd return get_user_where(id=id)
    # mgd return Users.query.filter_by(id=id).first()


@shared.login_manager.request_loader
def request_loader(request):
    username = "" if len(request.form) == 0 else request.form.get("username")
    user = None if is_str_none_or_empty(username) else get_user_where(username_lower=username.lower())
    return user


# eof
