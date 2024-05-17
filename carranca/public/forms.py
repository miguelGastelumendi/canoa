# Equipe da Canoa -- 2024
#  See .\carranca\private\forms.py
# mgd 2024-04-07
#
# cSpell: ignore: wtforms

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import Email, DataRequired, Length

# Public forms
# Text here ha no relevance, the ui_text table is actually used.

class LoginForm(FlaskForm):
    username = StringField('Username',
                     validators=[DataRequired(), Length(min=6)])
    password = PasswordField('Password',
                     validators=[DataRequired()])
    remember_me = BooleanField('Remember_me')


class RegisterForm(FlaskForm):
    username = StringField('Username',
                     validators=[DataRequired()])
    email = StringField('Email',
                     validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                     validators=[DataRequired(), Length(min=6)])
    disabled = BooleanField('Disabled')


class PasswordRecoveryForm(FlaskForm):
    user_email = StringField('Send link to this email',
                             validators=[DataRequired(), Email()])


#eof
