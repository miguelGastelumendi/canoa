"""
 Private Models

mgd
Equipe da Canoa -- 2024
"""

# Equipe da Canoa -- 2024
#
# cSpell:ignore: nullable sqlalchemy sessionmaker sep ssep scm sepsusr usrlist SQLA

from typing import List, Optional, Tuple
from sqlalchemy import (
    Boolean,
    Column,
    Computed,
    DateTime,
    Integer,
    String,
    Text,
    select,
    func,
    and_,
    exists,
)
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import defer, Session
from sqlalchemy.ext.hybrid import hybrid_property


from .. import global_sqlalchemy_scoped_session

from ..models import SQLABaseTable
from ..models.public import User
from ..private.SepIconConfig import SepIconConfig, svg_content
from ..common.app_context_vars import sidekick
from ..helpers.db_helper import db_fetch_rows, db_ups_error
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.user_helper import get_user_code
from ..helpers.db_records.DBRecords import DBRecords


# --- Table ---
class UserDataFiles(SQLABaseTable):
    """
    UserDataFiles is app's interface for the
    DB table `user_data_files` that works as a
    log of the validation process. Every step
    of the process (that starts with
    uploading a file and ends with sending an
    email with the validation report attached
    or displaying a error message)
    is recorded in one row.
    """

    __tablename__ = "user_data_files"

    # register, pk/fk/uniqueKey
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket = Column(String(40), unique=True)
    id_sep = Column(Integer)  # fk
    id_users = Column(Integer)  # fk

    # register, file info
    file_name = Column(String(80))
    file_size = Column(Integer)
    file_crc32 = Column(Integer)
    user_receipt = Column(String(14))

    # register, sys info
    db_version = Column(String(12))
    app_version = Column(String(12))
    process_version = Column(String(12))

    from_os = Column(String(1))
    file_origin = Column(String(1))
    original_name = Column(String(80), nullable=True, default=None)

    ## register
    a_received_at = Column(DateTime)
    b_process_started_at = Column(DateTime)
    c_check_started_at = Column(DateTime)
    d_register_started_at = Column(DateTime)

    ## submit & email & process
    e_unzip_started_at = Column(DateTime)
    f_submit_started_at = Column(DateTime)
    g_report_ready_at = Column(DateTime)

    ## submit
    validator_version = Column(String(8))
    validator_result = Column(String(280))
    report_errors = Column(Integer)
    report_warns = Column(Integer)
    report_tests = Column(Integer)

    ## submit & email
    h_email_started_at = Column(DateTime)

    ## email.py
    email_sent = Column(Boolean, default=False)

    ## process, on exit
    error_code = Column(Integer, nullable=True)
    error_msg = Column(String(200), nullable=True)
    error_text = Column(Text, nullable=True)
    success_text = Column(Text, nullable=True)
    z_process_end_at = Column(DateTime)

    ## Set on trigger
    # registered_at, at insert
    # db_version
    # email_sent_at, when email_sent = T
    # error_at, at error_code not 0
    # Special
    # error_handled, when admin handles the error (TODO)

    ## obsolete
    # upload_start_at ->
    # report_ready_ay -> g_report_ready_at
    #

    # Helpers
    @staticmethod
    def _get_record(db_session: Session, uTicket: str):
        """gets the record with unique key: uTicket"""
        stmt = select(UserDataFiles).where(UserDataFiles.ticket == uTicket)
        rows = db_session.scalars(stmt).all()
        if not rows:
            return None
        elif len(rows) == 1:
            return rows[0]
        else:
            raise KeyError(f"The ticket {uTicket} return several records, expecting only one.")

    @staticmethod
    def _ins_or_upd(isInsert: bool, uTicket: str, **kwargs) -> None:
        """insert or update a record with unique key: uTicket"""
        # action: insert/update
        isUpdate = not isInsert
        db_session: Session
        with global_sqlalchemy_scoped_session() as db_session:
            try:
                # if update, fetch existing record
                # if insert, check if record already exists
                record_to_ins_or_upd = UserDataFiles._get_record(db_session, uTicket)
                # check invalid conditions
                msg_exists = f"The ticket '{uTicket}' is " + "{0} registered."
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
        return None

    # Public insert/update
    def insert(uTicket: str, **kwargs) -> None:
        UserDataFiles._ins_or_upd(True, uTicket, **kwargs)
        return None

    def update(uTicket: str, **kwargs) -> None:
        UserDataFiles._ins_or_upd(False, uTicket, **kwargs)
        return None


# --- Table ---
class Schema(SQLABaseTable):

    __tablename__ = "vw_schema"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    user_lower = Column(String(100), Computed(""))
    description = Column(String(140))

    @staticmethod
    def get_schemas() -> DBRecords:
        def _get_data(db_session: Session):
            # When columns are selected, return is a record (List) of scalar
            stmt = select(Schema.id, Schema.name).order_by(Schema.name)
            schema_rows = db_session.execute(stmt).all()
            schema_recs = DBRecords(stmt, schema_rows)
            return schema_recs

        e, msg_error, schema_rows = db_fetch_rows(_get_data)
        if e:
            db_ups_error(e, msg_error, Schema.__tablename__)

        return schema_rows


# # --- Table --- Replaced by Public.User
# class SepUserData(SQLABaseTable):

#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True)
#     id_role = Column(Integer)
#     username = Column(String(100), unique=True)
#     username_lower = Column(String(100), Computed(""))
#     email = Column(String(64), unique=True)
#     disabled = Column(Boolean, default=False)


# --- Table ---
class MgmtSepsUser(SQLABaseTable):
    """
    `vw_mgmt_user_sep` is a database view designed to provide the necessary
    information for displaying a UI grid in the application's admin panel.

    This grid enables administrators to efficiently assign or remove users
    from SEPs (Setor Estratégico P...).

    The view is equipped with triggers that automatically update the `users`
    table and log the corresponding actions in the `log_user_sep` table.
    """

    __tablename__ = "vw_mgmt_seps_user"

    # SEP table
    id = Column(Integer, primary_key=True, autoincrement=False)  # like a PK
    name = Column(String(100))
    fullname = Column(String(256))  # schema + sep_name
    fullname_lower = Column(String(256))
    icon_file_name = Column(String(120))
    description = Column(String(140))
    visible = Column(Boolean)
    # Schema table
    scm_id = Column(Integer)
    scm_name = Column(String(100))
    # User table
    user_id = Column(Integer)
    user_disabled = Column(Boolean)
    user_curr = Column(String(100))
    user_new = Column(String(100))  #  pass through column: ' '

    assigned_at = Column(DateTime)  # sep.mgmt_users_at
    assigned_by = Column(Integer)  #  pass through column: 0
    batch_code = Column(String(10))  # pass through column: ' '

    # @staticmethod
    # def get_sepsusr_and_usrlist(
    #     field_names: Optional[List[str]], user_id: Optional[int] = None
    # ) -> Tuple[DBRecords, DBRecords]:
    #     """
    #     Returns
    #     1) `vw_mgmt_seps_user` DB view that has the necessary columns to
    #         provide the adm with a UI grid to assign or remove SEP
    #         to or from a user.
    #     2) list if users from `users`
    #     3) Error message if any action fails.
    #     """

    #     def _get_data(db_session: Session):
    #         def __cols() -> List[Column]:
    #             all_cols = MgmtSepsUser.__table__.columns
    #             _cols = [col for col in all_cols if col.name in field_names]
    #             return _cols

    #         sel_cols = __cols() if field_names else None
    #         stmt = select(*sel_cols) if sel_cols else select(MgmtSepsUser)
    #         if user_id is not None:  # then filter
    #             stmt = stmt.where(MgmtSepsUser.user_id == user_id)
    #             usr_list: DBRecords = []  # and there is no users list

    #         seps_rows = db_session.execute(stmt).all()
    #         seps_recs = DBRecords(stmt, seps_rows)

    #         if user_id is None:  # then get all users list, TODO: check 'disabled'?
    #             # stmt = select(SepUserData).order_by(SepUserData.username_lower)
    #             stmt = select(User.id, User.id_role, User.username, User.email, User.disabled).order_by(
    #                 User.username_lower
    #             )
    #             usr_rows = db_session.execute(stmt).all()
    #             usr_list = DBRecords(stmt, usr_rows)

    #         return seps_recs, usr_list

    #     e, msg_error, [seps_recs, usr_list] = db_fetch_rows(_get_data, 2)
    #     if e:
    #         db_ups_error(e, msg_error, MgmtSepsUser.__tablename__)

    #     return seps_recs, usr_list

    @staticmethod
    def get_seps_usr(field_names: Optional[List[str]], user_id: Optional[int] = None) -> DBRecords:
        """
        Returns
        1) `vw_mgmt_seps_user` DB view that has the necessary columns to
            provide the adm with a UI grid to assign or remove SEP
            to or from a user.
        2) Error message if any action fails.
        """

        def _get_data(db_session: Session):
            def __cols() -> List[Column]:
                all_cols = MgmtSepsUser.__table__.columns
                _cols = [col for col in all_cols if col.name in field_names]
                return _cols

            sel_cols = __cols() if field_names else None
            stmt = select(*sel_cols) if sel_cols else select(MgmtSepsUser)
            if user_id is not None:  # then filter
                stmt = stmt.where(MgmtSepsUser.user_id == user_id)

            seps_rows = db_session.execute(stmt).all()
            seps_recs = DBRecords(stmt, seps_rows)
            return seps_recs

        e, msg_error, seps_recs = db_fetch_rows(_get_data)
        if e:
            db_ups_error(e, msg_error, MgmtSepsUser.__tablename__)

        return seps_recs


# --- Table ---
class MgmtEmailSep(SQLABaseTable):
    """
    This *Updatable view `vw_mgmt_email_sep` exposes
    columns to assist in sending emails to users when
    the SEP assigned to them is changed by an admin.
        .\private\sep_mgmt\send_email.py
        updates email_at and email_error
    """

    __tablename__ = "vw_mgmt_email_sep"

    id = Column(Integer, primary_key=True, autoincrement=True)
    new_user_name = Column(String, Computed(""))  # read only columns
    new_user_email = Column(String, Computed(""))
    old_user_name = Column(String, Computed(""))
    old_user_email = Column(String, Computed(""))
    sep_fullname = Column(String, Computed(""))
    batch_code = Column(String(10))
    email_at = Column(DateTime)
    email_error = Column(String(400))


# # --- Table ---
# class SchemaSEP(SQLABaseTable):
#     """
#     Auxiliary View
#     SchemaSEP is app's interface for the
#     DB view `vw_scm_sep` that provides a couple of
#     columns
#     """

#     __tablename__ = "vw_scm_sep"
#     id = Column("sep_id", Integer, primary_key=True)
#     user_id = Column("user_id", Integer, primary_key=True)
#     sep_fullname = Column(Text)

#     # 2025.06.16
#     # not needed anymore
#     # @staticmethod
#     # def _get_sep_fullname(db_session: Session, sep_id: int) -> str:

#     #     stmt = select(SchemaSEP.sep_fullname).where(SchemaSEP.id == sep_id)
#     #     cell = db_session.execute(stmt).one_or_none()
#     #     sep_fullname = None if cell is None else cell
#     #     # AQUI
#     #     return sep_fullname

#     # @staticmethod
#     # def get_sep_fullname(sep_id: int) -> str:
#     #     if to_int(sep_id, -1) == -1:
#     #         return ""

#     #     e, msg_error, sep_fullname = db_fetch_rows(SchemaSEP._get_sep_fullname, sep_id)
#     #     if e:
#     #         db_ups_error(e, msg_error, Sep.__tablename__)

#     #     return sep_fullname


# --- Table ---
class Sep(SQLABaseTable):
    """
    Table `sep` keeps the basic information of
    each SEP
    """

    __tablename__ = "sep"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_schema = Column(Integer)
    users_id = Column("mgmt_users_id", Integer)
    ins_by = Column(Integer)
    ins_at = Column(DateTime)
    name = Column(String(100), unique=True, nullable=False)
    name_lower = Column(String(100), Computed(""), unique=True)
    description = Column(String(140), nullable=False)
    icon_file_name = Column(String(120), nullable=True)
    icon_uploaded_at = Column(DateTime, nullable=True)
    icon_version = Column(Integer, nullable=False)
    icon_original_name = Column(String(120), nullable=True)
    icon_svg = Column(Text, nullable=True)

    # const
    scm_sep = sidekick.config.SCM_SEP_SEPARATOR

    @staticmethod
    def get_fullname(scm_name: str, sep_name: str) -> str:
        return f"{scm_name}{Sep.scm_sep}{sep_name}"

    @staticmethod
    def get_sep(id: int, load_icon: Optional[bool] = False) -> "Sep":
        """
        Select a SEP by id, with deferred Icon content (useful for edition). It also
        returns the SEP's full name (schema +\+ SEP) from the view `vw_scm_sep`.

        NB:
            Forward Reference
            Optional['MgmtSep']
            using quotes around a type in type hints is known as a forward reference.
        """
        if id is None:
            return None

        def _get_data(db_session: Session) -> Sep:
            stmt = select(Sep).options(defer(Sep.icon_svg)).where(Sep.id == id)
            sep_row = db_session.execute(stmt).scalar_one_or_none()

            if sep_row and load_icon:
                db_session.refresh(sep_row, attribute_names=[Sep.icon_svg.name])

            return sep_row

        e, msg_error, sep_row = db_fetch_rows(_get_data)
        if e:
            db_ups_error(e, msg_error, Sep.__tablename__)

        return sep_row

    @staticmethod
    def get_content(id: int) -> Optional[svg_content]:
        """
        Returns the content of the icon_svg (useful for creating a file)
        """

        def _get_data(db_session: Session) -> svg_content:
            try:
                stmt = select(Sep).where(Sep.id == id)
                sep = db_session.execute(stmt).scalar_one_or_none()
                is_empty = is_str_none_or_empty(sep.icon_svg)
                icon_content = SepIconConfig.empty_content if is_empty else sep.icon_svg
            except Exception as e:
                icon_content = SepIconConfig.error_content
                sidekick.app_log.error(f"Error retrieving icon content of SEP {id}: [{e}].")
            return icon_content

        e, msg_error, icon_content = db_fetch_rows(_get_data)
        if e:
            db_ups_error(e, msg_error, Sep.__tablename__)

        return icon_content, msg_error

    @staticmethod
    def save(sep_row: "Sep") -> bool:
        """
        Saves a Sep record
        """
        done = False
        db_session: Session
        with global_sqlalchemy_scoped_session() as db_session:
            try:
                db_session.add(sep_row)
                db_session.commit()
                done = True
            except Exception as e:
                db_session.rollback()
                sidekick.display.error(f"Error saving SEP record: [{e}].")
                # msg_error = f"Cannot update {Sep.__tablename__}.id = {user_sep} | Error {e}."

        return done

    @staticmethod
    def this_name_exists(sep_name: str) -> bool:

        def _get_data(db_session: Session) -> svg_content:
            stmt = select(Sep.name_lower).where(Sep.name_lower == func.lower(sep_name))
            name_exists = db_session.query(exists(stmt)).scalar()
            return name_exists

        e, msg_error, name_exists = db_fetch_rows(_get_data)
        if e:
            db_ups_error(e, msg_error, Sep.__tablename__)

        return name_exists


# --- Table ---
class ReceivedFiles(SQLABaseTable):
    """
    ReceivedFiles is app's interface for the
    DB view `vw_user_data_files` that provides the needed
    information to manage the files uploaded by users.
    """

    __tablename__ = "vw_user_data_files"

    id = Column(Integer, primary_key=True)
    user_id = Column("id_users", Integer)  # index (user_id, registered_at)
    user_name = Column("username", String(100))
    user_email = Column("email", String(100))

    # file sep, when registered*
    file_sep_id = Column("id_sep", Integer)
    # Sep Id selected by the user to submit the file
    sep_id = Column(Integer)
    sep_fullname = Column(String(256))

    submitted_at = Column("registered_at", DateTime)  # index (user_id, registered_at)
    stored_file_name = Column(String(180))
    file_name = Column("original_name", String(80))
    file_origin = Column(String(1))
    file_size = Column(Integer)
    file_crc32 = Column(Integer)

    report_errors = Column(Integer)
    report_warns = Column(Integer)

    user_receipt = Column(String(15))
    email_sent = Column(Boolean)  # index (email_sent, had_reception_error, user_id, registered_at)
    had_reception_error = Column(Boolean)  # index (email_sent, had_reception_error, user_id, registered_at)

    @staticmethod
    def get_records(
        file_id: int, user_id: int, email_sent: bool = True, had_reception_error: bool = False
    ) -> DBRecords:

        def _get_rows(db_session: Session) -> DBRecords:
            """----------------------------------------------
            /!\ Attention
            -------------------------------------------------
                There is an index on the underlying table
                (email_sent, had_reception_error, user_id, registered_at)
                so if you are going change the where clause, be sure
                to include these fields.
            """
            stmt = select(ReceivedFiles)
            if file_id is not None:
                # For download, one file's id
                stmt = stmt.where(ReceivedFiles.id == file_id)
            else:
                # For grid
                stmt = stmt.where(
                    and_(
                        ReceivedFiles.email_sent == email_sent,
                        ReceivedFiles.had_reception_error == had_reception_error,
                    )
                )
                if user_id is not None:
                    stmt = stmt.where(ReceivedFiles.user_id == user_id)

            rows = db_session.execute(stmt).all()
            recs = DBRecords(stmt, rows)

            return recs

        e, msg_error, received_files = db_fetch_rows(_get_rows)
        if e:
            db_ups_error(e, msg_error, ReceivedFiles.__tablename__)

        return received_files


# --- Table ---
class ReceivedFilesCount(SQLABaseTable):
    """
    ReceivedFilesCount is app's interface for the
    DB view `vw_user_data_files_count` that provides the needed
    information to manage users that have send files
    """

    __tablename__ = "vw_user_data_files_count"

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(100))
    user_email = Column(String(100))
    rol_id = Column(Integer)
    rol_abbr = Column(String(3))
    rol_name = Column(String(64))
    files_count = Column(Integer)

    @hybrid_property
    def user_code(self):
        return get_user_code(self.user_id)

    @staticmethod
    def get_records(user_id: Optional[int] = None) -> DBRecords:
        def _get_data(db_session: Session) -> DBRecords:
            stmt = select(ReceivedFilesCount)  # stmt : Select[Tuple[ReceivedFilesCount]] =
            if user_id is not None:
                stmt = stmt.where(ReceivedFilesCount.user_id == user_id)

            rows = db_session.execute(stmt).all()
            recs = DBRecords(stmt, rows)

            return recs

        e, msg_error, received_files_count = db_fetch_rows(_get_data)
        if e:
            db_ups_error(e, msg_error, ReceivedFilesCount.__tablename__)

        return received_files_count


# eof
