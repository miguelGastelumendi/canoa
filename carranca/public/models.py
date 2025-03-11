"""
    Tables related to users
    Part of Public Access Control Processes

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore nullable sqlalchemy psycopg2 mgmt joinedload

from carranca import SqlAlchemyScopedSession, login_manager

from typing import Any
from psycopg2 import DatabaseError

from sqlalchemy import select
from sqlalchemy import Column, Computed, ForeignKey, Integer, String, DateTime, Boolean, LargeBinary
from sqlalchemy.orm import relationship, declarative_base, joinedload

# from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import UserMixin
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.pw_helper import hash_pass
from ..common.app_constants import APP_LANG
from ..private.roles_abbr import RolesAbbr

Base = declarative_base()


# --- Table ---
class User(Base, UserMixin):

    __tablename__ = "users"

    # https://docs.sqlalchemy.org/en/13/core/type_basics.html
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_role = Column(Integer, ForeignKey("roles.id"))
    lang = Column(String(8), default=APP_LANG)
    username = Column(String(100), unique=True)
    password = Column(LargeBinary)
    username_lower = Column(String(100), Computed(""))
    email = Column(String(64), unique=True)
    mgmt_sep_id = Column(Integer, unique=True)
    last_login_at = Column(DateTime, nullable=True)
    recover_email_token = Column(String(100), nullable=True, unique=True)
    recover_email_token_at = Column(DateTime, Computed(""))
    password_failures = Column(Integer, default=0)
    password_failed_at = Column(DateTime)

    disabled = Column(Boolean, default=False)
    email_confirmed = Column(Boolean, Computed("email_confirmed", persisted=True))

    role = relationship("Role", back_populates="users")

    # Here's how to use role_mame in Python instead of user.role.name
    # @hybrid_property
    # def role_name(self):
    #     return self.role.name if self.role else None

    # Here's how to use role_mame in an expression in SQLALchemy SQL (eg .filter(User.role_abbr == “ADM”).all()
    # @role_name.expression
    # def role_name(cls):  # For querying
    #     return Role.name

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


def get_user_where(**filter: Any) -> User:
    """
    Select a user by a unique filter
    """
    from ..common.app_context_vars import sidekick

    user = None
    with SqlAlchemyScopedSession() as db_session:
        try:
            # stmt = select(User).filter_by(**filter)
            # user =  db_session.execute(stmt).scalar_one_or_none()
            user = db_session.query(User).options(joinedload(User.role)).filter_by(**filter).first()
        except Exception as e:
            sidekick.app_log.error(f"Error retrieving user {filter}: [{e}].")

    return user


def persist_user(record: any, task_code: int = 1) -> None:
    """
    Updates a user's record
    """
    from ..common.app_context_vars import sidekick

    with SqlAlchemyScopedSession() as db_session:
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
    # current_user #
    user = get_user_where(id=id)
    return user


@login_manager.request_loader
def request_loader(request):
    username = "" if len(request.form) == 0 else request.form.get("username")
    user = None if is_str_none_or_empty(username) else get_user_where(username_lower=username.lower())
    return user


# --- Table ---
class Role(Base):
    """
    User's role in Canoa
    """

    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    abbr = Column(String(3))  # see user_roles.py
    users = relationship("User", back_populates="role")


def get_user_role_abbr(user_id: int, user_role_id: int) -> RolesAbbr:
    """
    Retrieves and checks a user role against enum
    """

    abbr = None
    if not user_role_id is None:
        with SqlAlchemyScopedSession() as db_session:
            try:
                row = db_session.query(Role).filter_by(id=user_role_id).first()
                abbr = None if row is None else row.abbr
            except Exception as e:
                from ..common.app_context_vars import sidekick

                sidekick.app_log.error(f"Error retrieving user {user_id} role {user_role_id}: [{e}].")

    return abbr


# eof
