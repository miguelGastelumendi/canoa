# -*- encoding: utf-8 -*-us
"""
 Equipe da Canoa -- 2024
 See .\carranca\home\forms.py

 mgd 2024-04-09,27
 ----------------------
"""
#cSpell: ignore: wtforms



from flask_wtf import FlaskForm
from wtforms import PasswordField, FileField
from wtforms.validators import DataRequired, Length, EqualTo



class NewPasswordForm(FlaskForm):
    password = PasswordField('Nova senha',
                     validators=[DataRequired(), Length(min=6), EqualTo('confirm_password', message="As senhas não são iguais.")])
                     # EqualTo não está funcionando 2024.03.21
    confirm_password = PasswordField('Confirme a nova senha',
                     validators=[DataRequired(), Length(min=6)])


class UploadFileForm(FlaskForm):
    filename = FileField('Arquivo', validators= [DataRequired()])


#eof