# -*- encoding: utf-8 -*-us
"""
 Equipe da Canoa -- 2024

 mgd 2024-04-09,27
 ----------------------
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FileField
from wtforms.validators import Email, DataRequired, Length, EqualTo

# login and registration

class LoginForm(FlaskForm):
    username = StringField('Username',
                     validators=[DataRequired()])
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

class NewPasswordForm(FlaskForm):
    password = PasswordField('Nova senha',
                     validators=[DataRequired(), Length(min=6), EqualTo('confirm_password', message="As senhas não são iguais.")])
                     # EqualTo não está funcionando 2024.03.21
    confirm_password = PasswordField('Confirme a nova senha',
                     validators=[DataRequired(), Length(min=6)])

class PasswordRecoveryForm(FlaskForm):
    user_email = StringField('Email para envio do link',
                             validators=[DataRequired(), Email()])

class UploadFileForm(FlaskForm):
    filename = FileField('Arquivo', validators= [DataRequired()])


#eof





# eof #