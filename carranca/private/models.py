"""
    Model of the table of files uploaded by users

    mgd
    Equipe da Canoa -- 2024
"""

# cSpell:ignore cuser Setorista

# Equipe da Canoa -- 2024
#
# cSpell:ignore: nullable psycopg2 sqlalchemy sessionmaker mgmt

from typing import Any, List, Tuple
from psycopg2 import DatabaseError, OperationalError
from sqlalchemy import select, text
from sqlalchemy import Boolean, Column, Computed, DateTime, Integer, String, Text
from sqlalchemy.orm import defer, Session as SQLAlchemySession

from sqlalchemy.ext.declarative import declarative_base
from carranca import SqlAlchemyScopedSession

from ..Sidekick import sidekick
from ..helpers.db_helper import TableRecords, TableEmpty
from ..helpers.py_helper import is_str_none_or_empty


# https://stackoverflow.com/questions/45259764/how-to-create-a-single-table-using-sqlalchemy-declarative-base
Base = declarative_base()


class UserDataFiles(Base):
    __tablename__ = "user_data_files"

    # keys (register..on_ins)
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket = Column(String(40), unique=True)
    user_receipt = Column(String(14))
    id_sep = Column(Integer)

    # sys version (register..on_ins)
    app_version = Column(String(12))
    process_version = Column(String(12))

    id_users = Column(Integer)  # fk
    # file info (register..on_ins)
    file_crc32 = Column(Integer)
    file_name = Column(String(80))
    file_origin = Column(String(1))
    file_size = Column(Integer)
    from_os = Column(String(1))
    original_name = Column(String(80), nullable=True, default=None)

    # Process module
    ## (register..on_ins)
    a_received_at = Column(DateTime)
    b_process_started_at = Column(DateTime)
    c_check_started_at = Column(DateTime)
    d_register_started_at = Column(DateTime)

    ## saved at email.py
    e_unzip_started_at = Column(DateTime)
    f_submit_started_at = Column(DateTime)
    g_email_started_at = Column(DateTime)

    z_process_end_at = Column(DateTime)

    # event
    ## saved at email.py
    email_sent = Column(Boolean, default=False)
    report_ready_at = Column(DateTime)

    # Set on trigger
    # registered_at, at insert
    # email_sent_at, when email_sent = T
    # error_at, at error_code not 0

    # obsolete
    # upload_start_at = Column(DateTime)

    error_code = Column(Integer, nullable=True)
    error_msg = Column(String(200), nullable=True)
    error_text = Column(Text, nullable=True)
    success_text = Column(Text, nullable=True)

    # Helpers
    def _get_record(session: SQLAlchemySession, uTicket):
        """gets the record with unique Key uTicket"""
        stmt = select(UserDataFiles).where(UserDataFiles.ticket == uTicket)
        rows = session.scalars(stmt).all()
        if not rows:
            return None
        elif len(rows) == 1:
            return rows[0]
        else:
            raise KeyError(f"The ticket {uTicket} return several records, expecting only one.")

    def _ins_or_upd(isInsert: bool, uTicket: str, **kwargs) -> None:
        isUpdate = not isInsert
        with SqlAlchemyScopedSession() as db_session:
            try:
                msg_exists = f"The ticket '{uTicket}' is " + "{0} registered."
                # Fetch existing record if update, check if record already exists if insert
                record_to_ins_or_upd = UserDataFiles._get_record(db_session, uTicket)
                # check invalid conditions
                if isUpdate and record_to_ins_or_upd is None:
                    raise KeyError(msg_exists.format("not"))
                elif isInsert and record_to_ins_or_upd is not None:
                    raise KeyError(msg_exists.format("already"))
                elif isInsert:
                    record_to_ins_or_upd = UserDataFiles(ticket=uTicket, **kwargs)
                    db_session.add(record_to_ins_or_upd)
                else:  # isUpdate
                    for attr, value in kwargs.items():
                        if value is not None:
                            setattr(record_to_ins_or_upd, attr, value)

                db_session.commit()
            except Exception as e:
                db_session.rollback()
                operation = "update" if isUpdate else "insert to"
                msg_error = (
                    f"Cannot {operation} {UserDataFiles.__tablename__}.ticket = {uTicket} | Error {e}."
                )
                sidekick.app_log.error(msg_error)
                raise DatabaseError(msg_error)

    # Public insert/update
    def insert(uTicket: str, **kwargs) -> None:
        UserDataFiles._ins_or_upd(True, uTicket, **kwargs)

    def update(uTicket: str, **kwargs) -> None:
        UserDataFiles._ins_or_upd(False, uTicket, **kwargs)


class MgmtUserSep(Base):
    """
    `vw_mgmt_user_sep` is view that provide the user
    with a UI grid to assign or remove SEP
    to or from a user.
    """

    __tablename__ = "vw_mgmt_user_sep"

    # https://docs.sqlalchemy.org/en/13/core/type_basics.html
    user_id = Column(Integer, primary_key=True, autoincrement=False)  # like a PK
    sep_id = Column(Integer)
    user_name = Column(String(100))
    user_disabled = Column(Boolean)
    scm_sep_curr = Column(String(201))  # sep_name -> scm_sep_curr
    scm_sep_new = Column(String(201))  # sep_new -> scm_sep_new
    assigned_at = Column(DateTime)
    assigned_by = Column(Integer)
    batch_code = Column(String(10))  # trace_code

    # Helpers
    def get_grid_view(item_none: str) -> Tuple[TableRecords, List[Tuple[str, str]], str]:
        """
        Returns the `vw_mgmt_user_sep` view with the necessary columns to
        provide the user with a UI grid to assign or remove SEP
        to or from a user.
        """
        from .sep_icon import icon_prepare_for_html

        msg_error = None
        with SqlAlchemyScopedSession() as db_session:
            users_sep = TableEmpty
            try:

                def _file_url(sep_id: int) -> str:
                    url, _, _ = icon_prepare_for_html(
                        sep_id
                    )  # this is foreach user (don't user logged_user)
                    return url

                sep_list = [
                    {"id": sep.sep_id, "fullname": sep.sep_fullname}
                    for sep in db_session.execute(
                        text(f"SELECT sep_id, sep_fullname FROM vw_scm_sep")
                    ).fetchall()
                ]
                users_sep = [
                    {
                        "user_id": usr_sep.user_id,
                        "sep_id": usr_sep.sep_id,
                        "file_url": _file_url(usr_sep.sep_id),
                        "user_name": usr_sep.user_name,
                        "disabled": usr_sep.user_disabled,
                        "scm_sep_curr": item_none if usr_sep.scm_sep_curr is None else usr_sep.scm_sep_curr,
                        "scm_sep_new": item_none,
                        "when": usr_sep.assigned_at,
                    }
                    for usr_sep in db_session.scalars(select(MgmtUserSep)).all()
                ]
            except Exception as e:
                msg_error = str(e)
                sidekick.display.error(msg_error)

        return users_sep, sep_list, msg_error


class MgmtEmailSep(Base):
    """
    Table `log_user_sep` logs the actions done
    on the UI grid by the adm.

    This `view vw_mgmt_email_sep` exposes columns
    to assist sending emails.
    """

    __tablename__ = "vw_mgmt_email_sep"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, Computed(""))
    user_name = Column(String, Computed(""))
    user_email = Column(String, Computed(""))
    sep_name_new = Column(String, Computed(""))
    sep_name_old = Column(String, Computed(""))
    email_at = Column(DateTime)
    email_error = Column(String(400))
    batch_code = Column(String(10), Computed(""))


class MgmtSep(Base):
    """
    Table `sep` keeps the basic information of
    each SEP
    """

    __tablename__ = "sep"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(140), nullable=False)
    icon_file_name = Column(String(120), nullable=True)
    icon_uploaded_at = Column(DateTime, nullable=True)
    icon_original_name = Column(String(120), nullable=True)
    icon_svg = Column(Text, nullable=True)

    def get_sep(id: int) -> Tuple[Any, str]:
        """
        Select a SEP by id, with deferred Icon content (useful for edit)
        """
        if id is None:
            return None, None

        sep = None
        sep_fullname = None
        with SqlAlchemyScopedSession() as db_session:
            try:
                stmt = select(MgmtSep).options(defer(MgmtSep.icon_svg)).where(MgmtSep.id == id)
                _sep = db_session.execute(stmt).scalar_one_or_none()
                stmt = text(f"SELECT sep_fullname FROM vw_scm_sep WHERE sep_id={_sep.id}")
                row = db_session.execute(stmt).one_or_none()
                sep_fullname = None if row is None else row[0]
                sep = _sep
            except (OperationalError, DatabaseError) as e:
                sidekick.app_log.error(f"Database connection error: {e}")
            except Exception as e:
                sidekick.app_log.error(f"Error fetching user SEP info: {e}")

        return sep, sep_fullname

    def db_content(id: int) -> Any:
        """
        Returns the content of the icon_svg (useful for write a file)
        """
        from .SepIconConfig import SepIconConfig
        from ..Sidekick import sidekick

        sep = None
        with SqlAlchemyScopedSession() as db_session:
            icon_content = None
            try:
                stmt = select(MgmtSep).where(MgmtSep.id == id)
                sep = db_session.execute(stmt).scalar_one_or_none()
                is_empty = is_str_none_or_empty(sep.icon_svg)
                icon_content = SepIconConfig.empty_content() if is_empty else sep.icon_svg
            except Exception as e:
                icon_content = SepIconConfig.error_content()
                sidekick.app_log.error(f"Error retrieving icon content of SEP {sep.id}: [{e}].")

        return icon_content

    def set_sep(sep) -> bool:
        """
        Save a Sep
        """
        from ..Sidekick import sidekick

        done = False
        msg_error = ""
        with SqlAlchemyScopedSession() as db_session:
            try:
                db_session.add(sep)
                db_session.commit()
                done = True
            except Exception as e:
                db_session.rollback()
                msg_error = f"Cannot update {MgmtSep.__tablename__}.id = {sep} | Error {e}."
                sidekick.app_log.error(msg_error)

        return done


class ReceivedFiles(Base):
    __tablename__ = "vw_user_data_files"

    id = Column(Integer, primary_key=True)
    id_users = Column(Integer)
    username = Column(String(100))
    email = Column(String(100))

    # file sep, when registered*
    id_sep = Column(Integer)
    # current user sep id*
    mgmt_sep_id = Column(Integer)

    registered_at = Column(DateTime)
    stored_file_name = Column(String(180))
    file_name = Column(String(80))

    file_size = Column(Integer)
    file_crc32 = Column(Integer)

    email_sent = Column(Boolean)
    reception_error = Column(Boolean)

    def get_user_records(
        user_id: int = None, if_email_sent: bool = True, if_has_reception_error: bool = False
    ) -> TableRecords:
        received_files: TableRecords = None
        with SqlAlchemyScopedSession() as db_session:
            try:
                stmt = select(ReceivedFiles).where(
                    ReceivedFiles.email_sent == if_email_sent,
                    ReceivedFiles.reception_error == if_has_reception_error,
                )
                if user_id is not None:
                    stmt = stmt.where(ReceivedFiles.id_users == user_id)

                received_files = [
                    {
                        "id": record.id,
                        "user_id": record.id_users,
                        "user_name": record.username,
                        "user_email": record.email,
                        "user_sep_id": record.mgmt_sep_id,
                        "file_sep_id": record.id_sep,
                        "received_at": record.registered_at,
                        "stored_file_name": record.stored_file_name,
                        "file_name": record.file_name,
                        "file_size": record.file_size,
                        "file_crc32": record.file_crc32,
                        "email_sent": record.email_sent,
                        "reception_error": record.reception_error,
                        "file_found": False,
                    }
                    for record in db_session.scalars(stmt).all()
                ]
            except Exception as e:
                msg_error = (
                    f"Cannot load records from {ReceivedFiles.__tablename__}.where = {stmt} | Error {e}."
                )
                sidekick.app_log.error(msg_error)

        return received_files


# eof
