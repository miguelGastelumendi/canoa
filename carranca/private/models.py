"""
    Model of the table of files uploaded by users

    mgd
    Equipe da Canoa -- 2024
    cSpell:ignore cuser
"""

# Equipe da Canoa -- 2024
#
# cSpell:ignore: nullable

from carranca import db
from carranca.helpers.db_helper import persist_record


class UserDataFiles(db.Model):
    __tablename__ = "user_data_files"

    id = db.Column(db.Integer, primary_key=True)
    id_users = db.Column(db.Integer)
    file_name = db.Column(db.String(80))
    original_name = db.Column(db.String(80), nullable=True, default=None)
    file_size = db.Column(db.Integer)
    file_crc32 = db.Column(db.Integer)
    from_os = db.Column(db.String(1))
    ticket = db.Column(db.String(40))
    user_receipt = db.Column(db.String(14))

    # Process module
    ## saved at register.py
    a_received_at = db.Column(db.DateTime)
    b_process_started_at = db.Column(db.DateTime)
    c_check_started_at = db.Column(db.DateTime)
    d_register_started_at = db.Column(db.DateTime)
    ## saved at email.py
    e_unzip_started_at = db.Column(db.DateTime)
    f_submit_started_at = db.Column(db.DateTime)
    g_email_started_at = db.Column(db.DateTime)

    z_process_end_at = db.Column(db.DateTime)

    # event
    ## saved at email.py
    email_sent = db.Column(db.Boolean, default=False)
    report_ready_at = db.Column(db.DateTime)

    # Set on trigger
    # registered_at, at insert
    # email_sent_at, at email_sent = T
    # error_at, at error_code not 0

    # obsolete
    # upload_start_at = db.Column(db.DateTime)

    error_code = db.Column(db.Integer, nullable=True)
    error_msg = db.Column(db.String(200), nullable=True)
    error_text = db.Column(db.Text, nullable=True)
    success_text = db.Column(db.Text, nullable=True)

    def update(uTicket, **kwargs):
        result = False
        try:
            records = db.session.query(UserDataFiles).filter_by(ticket=uTicket)
            record_to_update = None if records is None else records.first()
            if not records or records.count() == 0:
                raise KeyError(f"The ticket {uTicket} is not registered.")
            elif records.count() > 1:
                raise KeyError(
                    f"The ticket {uTicket} return several records, expecting only one."
                )
            elif record_to_update:
                for attr, value in kwargs.items():
                    setattr(record_to_update, attr, value)

                persist_record(db, record_to_update)

        except Exception as e:
            raise RuntimeError(
                f"Cannot update {UserDataFiles.__tablename__}.ticket = {uTicket} | Error {e}."
            )

        return result


# eof
