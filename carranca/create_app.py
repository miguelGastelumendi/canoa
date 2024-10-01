# do_app.py
"""
  A slight modification to the standard __init__.py
  db (SQLAlchemy) & login_manager are created in
  'shared.py' file, where very common shred objects are,
  inclusive 'app'

Equipe Canoa -- 2024
"""

print('Module is starting...')
def create_app(config):
    from flask import Flask
    # https://flask.palletsprojects.com/en/latest/tutorial/factory/
    app = Flask(__name__)
    app.config.from_object(config)

    from .shared import shared
    shared.initialize(app, config)
    shared.bind()

    return app
# eof

