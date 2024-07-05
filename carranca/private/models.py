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
    __tablename__ = 'user_data_files'

    id = db.Column(db.Integer, primary_key=True)
    id_users = db.Column(db.Integer)
    file_name = db.Column(db.String(140))
    file_size = db.Column(db.Integer)
    file_crc32 = db.Column(db.Integer)
    from_os = db.Column(db.String(1))        
    ticket = db.Column(db.String(40))
    user_receipt = db.Column(db.String(14))
    upload_start_at = db.Column(db.DateTime)
    report_ready_at = db.Column(db.DateTime)
    email_sent = db.Column(db.Boolean, default=False)
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
