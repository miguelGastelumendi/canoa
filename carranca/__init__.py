#
# Equipe Canoa -- 2024
# cSpell:ignore sqlalchemy

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

def register_jinja(app, config):
    from .helpers.route_helper import private_route, public_route
    def __app_name() -> str:
        return config.app_name
    def __app_version() -> str:
        return config.app_version
    app.jinja_env.globals.update(
        private_route= private_route,
        public_route= public_route,
        app_name = __app_name,
        app_version = __app_version,
    )


def create_app(config):
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    register_jinja(app, config)
    return app

#eof