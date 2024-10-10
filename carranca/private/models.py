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
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
# TODO: from sqlalchemy.ext.declarative import declarative_base

from ..main import shared
from ..helpers.db_helper import persist_record


class UserDataFiles(shared.sa.Model):
    __tablename__ = "user_data_files"

    id = Column(Integer, primary_key=True)
    ticket = Column(String(40), unique=True)
    id_users = Column(Integer)   # fk

    app_version = Column(String(12))
    process_version = Column(String(12))

    file_name = Column(String(80))
    original_name = Column(String(80), nullable=True, default=None)
    file_size = Column(Integer)
    file_crc32 = Column(Integer)
    from_os = Column(String(1))
    file_origin = Column(String(1))
    user_receipt = Column(String(14))

    # Process module
    ## saved at register.py
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
    # email_sent_at, at email_sent = T
    # error_at, at error_code not 0

    # obsolete
    # upload_start_at = Column(DateTime)

    error_code = Column(Integer, nullable=True)
    error_msg = Column(String(200), nullable=True)
    error_text = Column(Text, nullable=True)
    success_text = Column(Text, nullable=True)

    # Helpers
    def _get_record(session, uTicket):
        ''' gets the record with unique Key uTicket '''
        # TODO: Where
        # https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html#sqlalchemy.orm.Query.filter
        records = session.query(UserDataFiles).filter_by(ticket=uTicket)
        if (records is None) or (records.count() == 0):
            record = None
        elif records.count() == 1:
            record= records.first()
        else:
            raise KeyError(f"The ticket {uTicket} return several records, expecting only one.")

        return record

    def _ins_or_upd(isInsert: bool, uTicket: str, **kwargs) -> None:
        isUpdate = not isInsert
        with shared.doSession() as session:
            try:
                msg_exists= f"The ticket '{uTicket}' is " + "{0} registered."
                record_to_ins_or_upd= UserDataFiles._get_record(session, uTicket)
                if isUpdate and record_to_ins_or_upd is None:
                    raise KeyError(msg_exists.format('not'))
                elif isInsert and record_to_ins_or_upd is not None:
                    raise KeyError(msg_exists.format('already'))
                elif isInsert:
                    record_to_ins_or_upd = UserDataFiles(ticket=uTicket)

                for attr, value in kwargs.items():
                    if value is not None:
                        setattr(record_to_ins_or_upd, attr, value)

                session.add(record_to_ins_or_upd)
                session.commit()
            except Exception as e:
                if session:
                    session.rollback()
                operation = 'update' if isUpdate else 'insert to'
                msg_error = f"Cannot {operation} {UserDataFiles.__tablename__}.ticket = {uTicket} | Error {e}."
                shared.app_log.error(msg_error)
                raise DatabaseError(msg_error)

    # Public insert/update
    def insert(uTicket: str, **kwargs) -> None:
        UserDataFiles._ins_or_upd(True, uTicket, **kwargs)

    def update(uTicket: str, **kwargs) -> None:
        UserDataFiles._ins_or_upd(False, uTicket, **kwargs)

# eof