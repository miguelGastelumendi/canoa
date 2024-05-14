# -*- encoding: utf-8 -*-us
"""
 Equipe da Canoa -- 2024

 See: .\carranca\authentication\forms.py
 mgd 2024-05-13
 ----------------------
"""
#cSpell: ignore: wtforms

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import Email, DataRequired, Length

# login and registration

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
    user_email = StringField('Email para envio do link',
                             validators=[DataRequired(), Email()])


#eof
