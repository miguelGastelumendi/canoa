# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from carranca import db, login_manager
from util import hash_pass


class UserDataFiles(db.Model):
    __tablename__ = 'user_data_files'

    id = db.Column(db.Integer, primary_key=True)
    id_users = db.Column(db.Integer)
    file_size = db.Column(db.Integer)
    file_crc32 = db.Column(db.Integer)
    file_name = db.Column(db.String(140))
    ticket = db.Column(db.String(40))
    error_code = db.Column(db.Integer)
    error_msg = db.Column(db.String(200))

    def update(uTicket, **kwargs):
        try:
            record_to_update = db.session.query(UserDataFiles).filter_by(ticket= uTicket).first()
            if record_to_update:
                for attr, value in kwargs.items():
                    setattr(record_to_update, attr, value)

            db.session.commit()
        except Exception as e:
            print( f"Cannot update {UserDataFiles.__tablename__}.ticket = {uTicket} | Error {e}.")



class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    username_lower = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)
    recover_email_token = db.Column(db.String(100))
    disabled = db.Column(db.Boolean)


    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
   if len(request.form) == 0 or request.form.get('username') == None:
      return None # mgd

   username = request.form.get('username')
   user = Users.query.filter_by(username_lower = username.lower()).first()
   return user if user else None


