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

from ..common.app_context_vars import sidekick, app_user

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


# Private form
class SepEdit(FlaskForm):
    schema_list = SelectField("", validators=[DataRequired()], render_kw={"class": "form-select"})
    schema_name = StringField(
        "",
        validators=[Length(min=5, max=140)],  # TODO sidekick.config.DB_len_val_for_sep
        render_kw={
            "class": "form-control",
            "required": False,
            "disabled": True,
            "autocomplete": "off",
        },
    )
    sep_name = StringField(
        "",
        validators=[Length(min=5, max=140)],  # TODO sidekick.config.DB_len_val_for_sep
        render_kw={
            "class": "form-control",
            "required": False,
            "disabled": True,
            "autocomplete": "off",
            "spellcheck": "true",
            "lang": f"{app_user.lang}",
        },
    )
    description = StringField(
        "",
        validators=[InputRequired(), Length(min=5, max=140)],
        render_kw={
            "class": "form-control",
            "id": "description",
            "autocomplete": "off",
            "spellcheck": "true",
            "lang": f"{app_user.lang}",
        },
    )
    icon_filename = FileField("", render_kw={"class": "form-control", "accept": ".svg"})


class SepNew(SepEdit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sep_name.render_kw["required"] = True
        self.sep_name.render_kw["disabled"] = False
        self.schema_list.validators.append(InputRequired())


# eof
