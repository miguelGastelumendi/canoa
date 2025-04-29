"""
*wtforms* HTML forms
Part of Private Access Control & `File Validation` Processes

Equipe da Canoa -- 2024
mgd 2024-04-09,27; 06-22
"""

# cSpell:ignore: wtforms urlname iconfilename

from wtforms import PasswordField, FileField, StringField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, URL

from ..common.app_context_vars import sidekick

# -------------------------------------------------------------
# Text here ha no relevance, the ui_text table is actually used.


# Private form
class ReceiveFileForm(FlaskForm):
    filename = FileField("", render_kw={"class": "form-control", "id": "upload_file", "accept": ".zip"})
    urlname = StringField("", validators=[URL()], render_kw={"class": "form-control", "id": "link_file"})


# Private & Public form
class ChangePassword(FlaskForm):
    password = PasswordField(
        "",
        validators=[InputRequired(), Length(**sidekick.config.DB_len_val_for_pw.wtf_val())],
        render_kw={"class": "form-control", "id": "pwdCreate"},
    )
    # , EqualTo('confirm_password', message="As senhas não são iguais.") é no servidor.

    confirm_password = PasswordField(
        "",
        validators=[InputRequired(), Length(**sidekick.config.DB_len_val_for_pw.wtf_val())],
        render_kw={"class": "form-control", "id": "pwdConfirm", "for": "pwdConfirm"},
    )


class SepEdit(FlaskForm):

    name = StringField(
        "",
        validators=[InputRequired()],
        render_kw={"class": "form-control", "id": "name", "readonly": None},
    )  # TODO **max_name.wtf_val())],
    description = StringField(
        "",
        validators=[InputRequired(), Length(min=5, max=140)],
        render_kw={"class": "form-control", "id": "description"},
    )
    icon_filename = FileField(
        "", render_kw={"class": "form-control", "id": "iconfilename", "accept": ".svg"}
    )

    # def __init__(self, *args, for_edit=False, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if for_edit:
    #         self.name.render_kw["readonly"] = True
    #     else:
    #         self.name.render_kw.pop("readonly", None)


# eof
