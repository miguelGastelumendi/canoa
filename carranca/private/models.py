# Equipe da Canoa -- 2024
#
# cSpell:ignore: nullable

from carranca import db

class UserDataFiles(db.Model):
    __tablename__ = 'user_data_files'

    id = db.Column(db.Integer, primary_key=True)
    id_users = db.Column(db.Integer)
    file_name = db.Column(db.String(140))
    file_size = db.Column(db.Integer)
    file_crc32 = db.Column(db.Integer)
    ticket = db.Column(db.String(40))
    upload_start_at = db.Column(db.DateTime)
    report_ready_at  = db.Column(db.DateTime)
    email_sent =  db.Column(db.Boolean, default=False)
    error_code = db.Column(db.Integer, nullable=True )
    error_msg = db.Column(db.String(200), nullable=True)
    error_text = db.Column(db.Text, nullable=True)
    success_text = db.Column(db.Text, nullable=True)

    def update(uTicket, **kwargs):
        result = False
        try:
            user_record_to_update = db.session.query(UserDataFiles).filter_by(ticket= uTicket).first()
            if user_record_to_update:
                for attr, value in kwargs.items():
                    setattr(user_record_to_update, attr, value)

            db.session.add(user_record_to_update)
            db.session.commit()
            result = True
        except Exception as e:
            raise RuntimeError( f"Cannot update {UserDataFiles.__tablename__}.ticket = {uTicket} | Error {e}.")

        return result

#eof


