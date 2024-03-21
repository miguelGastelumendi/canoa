# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired, Length, EqualTo

# login and registration


class LoginForm(FlaskForm):
    username = StringField('Username',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = StringField('Username',
                         id='username_create',
                         validators=[DataRequired()])
    email = StringField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])

class ChangePasswordForm(FlaskForm):
    password = PasswordField('Nova senha',
                             validators=[DataRequired(), Length(min=6), EqualTo('confirm_password', message="As senhas não são iguais.")])
    confirm_password = PasswordField('Confirme a nova senha',
                             validators=[DataRequired(), Length(min=6)])

class GetUserEmailForm(FlaskForm):
    user_email = StringField('Email para envio do link',
                             id='user_email',
                             validators=[DataRequired(), Email()])
