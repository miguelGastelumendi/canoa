# __init__.pt
"""
  A slight modification to the standard __init__.py
  db (SQLAlchemy) & login_manager are created in
  'shared.py' file, where very common shred objects are,
  inclusive 'app'

Equipe Canoa -- 2024
"""


def create_app():
    from flask import Flask
    from .shared import db, login_manager

    app = Flask(__name__)
    db.init_app(app)
    login_manager.init_app(app)
    return app

# eof