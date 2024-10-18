"""
    Model of the table of files uploaded by users

    mgd
    Equipe da Canoa -- 2024
    cSpell:ignore cuser
"""

# Equipe da Canoa -- 2024
#
# cSpell:ignore: nullable psycopg2 sqlalchemy sessionmaker

from psycopg2 import DatabaseError
from sqlalchemy import select
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from ..main import shared

# https://stackoverflow.com/questions/45259764/how-to-create-a-single-table-using-sqlalchemy-declarative-base
Base = declarative_base()


class UserDataFiles(Base):
    __tablename__ = "user_data_files"

    # keys (register..on_ins)
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_users = Column(Integer)  # fk
    ticket = Column(String(40), unique=True)
    user_receipt = Column(String(14))

    # sys version (register..on_ins)
    app_version = Column(String(12))
    process_version = Column(String(12))

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
    def _get_record(session, uTicket):
        """gets the record with unique Key uTicket"""
        statement = select(UserDataFiles).where(UserDataFiles.ticket == uTicket)
        rows = session.scalars(statement).all()
        if not rows:
            return None
        elif len(rows) == 1:
            return rows[0]
        else:
            raise KeyError(f"The ticket {uTicket} return several records, expecting only one.")

    def _ins_or_upd(isInsert: bool, uTicket: str, **kwargs) -> None:
        isUpdate = not isInsert
        with Session(shared.sa_engine()) as session:
            try:
                msg_exists = f"The ticket '{uTicket}' is " + "{0} registered."
                # Fetch existing record if update, check if record already exists if insert
                record_to_ins_or_upd = UserDataFiles._get_record(session, uTicket)
                # check invalid conditions
                if isUpdate and record_to_ins_or_upd is None:
                    raise KeyError(msg_exists.format("not"))
                elif isInsert and record_to_ins_or_upd is not None:
                    raise KeyError(msg_exists.format("already"))
                elif isInsert:
                    record_to_ins_or_upd = UserDataFiles(ticket=uTicket, **kwargs)
                    session.add(record_to_ins_or_upd)
                else:
                    for attr, value in kwargs.items():
                        if value is not None:
                            setattr(record_to_ins_or_upd, attr, value)

                session.commit()
            except Exception as e:
                operation = "update" if isUpdate else "insert to"
                msg_error = (
                    f"Cannot {operation} {UserDataFiles.__tablename__}.ticket = {uTicket} | Error {e}."
                )
                shared.app_log.error(msg_error)
                raise DatabaseError(msg_error)

    # Public insert/update
    def insert(uTicket: str, **kwargs) -> None:
        UserDataFiles._ins_or_upd(True, uTicket, **kwargs)

    def update(uTicket: str, **kwargs) -> None:
        UserDataFiles._ins_or_upd(False, uTicket, **kwargs)


# eof
