"""
*wtforms* HTML forms
Part of Private Access Control & `File Validation` Processes

Equipe da Canoa -- 2024
mgd 2024-04-09,27; 06-22
"""

# cSpell:ignore: wtforms urlname iconfilename uploadfile tmpl

from wtforms import PasswordField, FileField, StringField, SelectField, BooleanField, TextAreaField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, DataRequired, Length, URL

from ..common.app_context_vars import sidekick

# -------------------------------------------------------------
# Text here has no relevance, the ui_text table is actually used.


# _ ⚠️ _________________________________________________
#  Keep "name" and "id" the same string
#  or don't specified "id"
#
#  Because {{ schema_sep.id }} will render the name
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
    """
    ------------------------------------------------------------
       ⚠️
        Don't defined here mutable render_kw, they persist
        set value to those that will not change throw tha app
        see:
            carranca/private/sep_new_edit.py
                tmpl_form = SepNew(request.form) if is_new
                            else SepEdit(request.form)
    ------------------------------------------------------------
        like:
          lang, disabled, readonly, required
    """

    manager_name = StringField(
        "",
        render_kw={"class": "form-control", "disabled": True},  # always disabled
    )

    schema_name = StringField(
        "",
        validators=[Length(min=5, max=140)],  # TODO sidekick.config.DB_len_val_for_sep
        render_kw={"class": "form-control", "disabled": True},  # almost always disabled
    )

    sep_name = StringField(
        "",
        validators=[Length(min=5, max=140)],  # TODO sidekick.config.DB_len_val_for_sep
        render_kw={
            "class": "form-control",
            "autofocus": "true",
            "autocomplete": "off",
            "spellcheck": True,
            "lang": "",
        },
    )

    description = StringField(
        "",
        validators=[InputRequired(), Length(min=5, max=140)],
        render_kw={
            "class": "form-control",
            "autocomplete": "off",
            "spellcheck": True,
            "lang": "",  # ⚠️ Don't defined here, they persist. See below SepNew
        },
    )
    icon_filename = FileField("", render_kw={"class": "form-control", "accept": ".svg"})


# Derived Private form
class SepNew(SepEdit):
    schema_list = SelectField(
        "",
        validators=[DataRequired()],
        coerce=int,
        render_kw={"class": "form-select"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.schema_list.validators.append(InputRequired())


# Private form
class ScmEdit(FlaskForm):
    """
    ------------------------------------------------------------
       ⚠️
        Don't defined here mutable render_kw, they persist
        set value to those that will not change throw tha app
        see:
            carranca/private/sep_new_edit.py
                tmpl_form = SepNew(request.form) if is_new
                            else SepEdit(request.form)
    ------------------------------------------------------------
        like:
          lang, disabled, readonly, required
    """

    name = StringField(
        "",
        validators=[InputRequired(), Length(min=5, max=140)],  # TODO sidekick.config.DB_len_val_for_sep
        render_kw={
            "class": "form-control",
            "autofocus": "true",
            "autocomplete": "off",
            "spellcheck": True,
            "lang": "",
        },
    )

    visible = BooleanField(
        "",
        render_kw={"class": "form-check-input"},
    )

    color = StringField(
        "",
        validators=[Length(min=5, max=140)],
        render_kw={
            "class": "form-control",
            "autocomplete": "off",
            "spellcheck": False,
        },
    )

    title = StringField(
        "",
        validators=[InputRequired(), Length(min=5, max=140)],  # TODO sidekick.config.DB_len_val_for_sep
        render_kw={
            "class": "form-control",
            "autocomplete": "off",
            "spellcheck": True,
            "lang": "",
        },
    )

    description = StringField(
        "",
        validators=[Length(min=5, max=140)],
        render_kw={
            "class": "form-control",
            "autocomplete": "off",
            "spellcheck": True,
            "lang": "",  # ⚠️ Don't defined here, they persist. See below SepNew
        },
    )

    content = TextAreaField("", render_kw={"class": "form-control", "rows": "6"})


# eof
