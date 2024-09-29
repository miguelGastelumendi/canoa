# Package/__init__.py
# This file, is execute by the Python interpreter on startup once
"""
  A slight modification to the standard __init__.py
  db (SQLAlchemy) & login_manager are created in
  'shared.py' file, where very common shred objects are,
  inclusive 'app'

Equipe Canoa -- 2024
"""

def create_app(config):
    from flask import Flask
    # https://flask.palletsprojects.com/en/latest/tutorial/factory/
    app = Flask(__name__, instance_path= 'D:/Projects/AdaptaBrasil/canoa')
    app.config.from_object(config)

    from shared import shared
    shared._initialize(app, config)
    shared._bind()

    return app
# eof