# Equipe da Canoa -- 2024
# public\models.py
#
# mgd
# cSpell:ignore
"""
    *Users*
    Part of Public Authentication Processes
"""

from flask_login import UserMixin
from carranca import db, login_manager
from ..helpers.pw_helper import hash_pass


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
                # the ,= unpack of a singleton fails PEP8 (tra_vis flake8 test)
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
