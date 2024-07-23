"""
    *wtforms* HTML forms
    Part of Private Access Control & `File Validation` Processes

    Equipe da Canoa -- 2024
    mgd 2024-04-09,27; 06-22
"""
# cSpell:ignore: wtforms

from flask_wtf import FlaskForm
from wtforms import PasswordField, FileField
from wtforms.validators import InputRequired, Length, EqualTo
from ..shared import app_config

# -------------------------------------------------------------
# Text here ha no relevance, the ui_text table is actually used.

# Private form
class UploadFileForm(FlaskForm):
    filename = FileField('', validators= [InputRequired()])

# Private & Public form
class ChangePassword(FlaskForm):
    password = PasswordField('',
                    validators=[InputRequired(), Length(**app_config.len_val_for_pw.wtf_val())])
                    #, EqualTo('confirm_password', message="As senhas não são iguais.") é no servidor.

    confirm_password = PasswordField('',
                    validators=[InputRequired(), Length(**app_config.len_val_for_pw.wtf_val())])

# eof