#
# Equipe Canoa -- 2024
# cSpell:ignore sqlalchemy

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()

def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    #  for module_name in ('authentication', 'home'):
    #      module = import_module('carranca.{}.routes'.format(module_name))
    #      app.register_blueprint(module.blueprint)
    from .private.routes import bp_private #carranca\private\routes.py", line 16
    from .public.routes import bp_public
    app.register_blueprint(bp_private)
    app.register_blueprint(bp_public)


def configure_database(app):
    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app


#eof