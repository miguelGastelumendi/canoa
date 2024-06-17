#
# Equipe Canoa -- 2024
# cSpell:ignore sqlalchemy

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def register_extensions(app):
# db= None??    from flask_sqlalchemy import SQLAlchemy
 #   db = SQLAlchemy()
    db.init_app(app)
#    from flask_login import LoginManager
#    login_manager = LoginManager()
    login_manager.init_app(app)


def register_blueprints(app):
    from .private.routes import bp_private # carranca\private\routes.py
    app.register_blueprint(bp_private)
    from .public.routes import bp_public   # carranca\public\routes.py
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