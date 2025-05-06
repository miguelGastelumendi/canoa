"""
*wtforms* HTML forms
Part of Private Access Control & `File Validation` Processes

Equipe da Canoa -- 2024
mgd 2024-04-09,27; 06-22
"""

# cSpell:ignore: wtforms urlname iconfilename uploadfile

from wtforms import PasswordField, FileField, StringField, SelectField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, DataRequired, Length, URL

from ..common.app_context_vars import sidekick

# -------------------------------------------------------------
# Text here has no relevance, the ui_text table is actually used.


# _ /!\ _________________________________________________
#  Keep "name" and "id" the same string
#  or don't specified "id"
#
#  Because {{ schema_sep.id }} will rendered the name
#  But {{ schema_sep.render_kw.id }} will write the id.
# ________________________________________________________


# Private form
class ReceiveFileForm(FlaskForm):
    schema_sep = SelectField("", validators=[DataRequired()], render_kw={"class": "form-select"})
    uploadfile = FileField("", render_kw={"class": "form-control", "accept": ".zip"})
    urlname = StringField("", validators=[URL()], render_kw={"class": "form-control"})


# Private & Public form
class ChangePassword(FlaskForm):
    password = PasswordField(
        "",
        validators=[InputRequired(), Length(**sidekick.config.DB_len_val_for_pw.wtf_val())],
        render_kw={"class": "form-control"},
    )

    confirm_password = PasswordField(
        "",
        validators=[InputRequired(), Length(**sidekick.config.DB_len_val_for_pw.wtf_val())],
        render_kw={"class": "form-control"},
    )


class SepEdit(FlaskForm):

    name = StringField(
        "",
        render_kw={
            "class": "form-control",
            "disabled": True,
        },
    )
    # TODO **max_name.wtf_val())],
    description = StringField(
        "",
        validators=[InputRequired(), Length(min=5, max=140)],
        render_kw={"class": "form-control", "id": "description"},
    )
    icon_filename = FileField("", render_kw={"class": "form-control", "accept": ".svg"})


# eof
