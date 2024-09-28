# carranca/__init__.py
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
    app = Flask(__name__)
    app.config.from_object(config)

    from .shared import do_db_and_shared_objects
    do_db_and_shared_objects(app, config)

    return app

# eof