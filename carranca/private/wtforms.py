"""
    *wtforms* HTML forms
    Part of Private Access Control & `File Validation` Processes

    Equipe da Canoa -- 2024
    mgd 2024-04-09,27; 06-22
"""
# cSpell:ignore: wtforms urlname

from flask_wtf import FlaskForm
from wtforms import PasswordField, FileField, StringField
from wtforms.validators import InputRequired, Length, URL
from ..shared import shared as g

# -------------------------------------------------------------
# Text here ha no relevance, the ui_text table is actually used.

# Private form
class ReceiveFileForm(FlaskForm):
    filename = FileField('', render_kw={"class": "form-control", "id": "upload_file", "accept": ".zip"})
    urlname = StringField('', validators=[URL()], render_kw={"class": "form-control", "id": "link_file"})

# Private & Public form
class ChangePassword(FlaskForm):
    password = PasswordField('',
                    validators=[InputRequired(), Length(**g.app_config.len_val_for_pw.wtf_val())])
                    #, EqualTo('confirm_password', message="As senhas não são iguais.") é no servidor.

    confirm_password = PasswordField('',
                    validators=[InputRequired(), Length(**g.app_config.len_val_for_pw.wtf_val())])

# eof