#
# Equipe Canoa -- 2024
# cSpell:ignore sqlalchemy

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

# eof