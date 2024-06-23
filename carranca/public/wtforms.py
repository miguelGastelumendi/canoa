"""
    *wtforms* HTML forms
    Part of Public Access Control Processes

    Equipe da Canoa -- 2024
    mgd 2024-04-09,27; 06-22
"""

# cSpell:ignore: wtforms


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import Email, InputRequired, Length
from main import app_config


# Public forms
# -------------------------------------------------------------
# Text here ha no relevance, the ui_text table is actually used.


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[InputRequired(), Length(**app_config.len_val_for_uname.wtf_val())],
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(**app_config.len_val_for_pw.wtf_val())],
    )
    remember_me = BooleanField("Remember_me")


class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[InputRequired(), Length(**app_config.len_val_for_uname.wtf_val())],
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(**app_config.len_val_for_pw.wtf_val())],
    )
    disabled = BooleanField("Disabled")


class PasswordRecoveryForm(FlaskForm):
    user_email = StringField(
        "Send link to this email",
        validators=[InputRequired(), Email()]
    )


# eof
