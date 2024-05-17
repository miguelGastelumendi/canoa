# Equipe da Canoa -- 2024
#  See .\carranca\public\forms.py
#
# mgd 2024-04-09,27
# cSpell: ignore: wtforms

from flask_wtf import FlaskForm
from wtforms import PasswordField, FileField
from wtforms.validators import DataRequired, Length, EqualTo

# Text here ha no relevance, the ui_text table is actually used.

# Private form
class UploadFileForm(FlaskForm):
    filename = FileField('Arquivo',
                    validators= [DataRequired()])

# Private & Public form
class NewPasswordForm(FlaskForm):
    password = PasswordField('Nova senha',
                    validators=[DataRequired(), Length(min=6), EqualTo('confirm_password', message="As senhas não são iguais.")])
                    # TODO EqualTo is not working 2024.03.21

    confirm_password = PasswordField('Confirme a nova senha',
                    validators=[DataRequired(), Length(min=6)])


#eof