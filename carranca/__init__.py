"""
    Package/__init__.py
    `This file, is execute by the Python interpreter on startup once`



    Equipe da Canoa -- 2024
    mgd

"""

# cSpell:ignore app_name sqlalchemy sessionmaker autoflush

# ============================================================================ #
# Public/Global variables
login_manager = None
SqlAlchemySession = None
Config = None
app = None

# Module variable
import time

started = time.perf_counter()

# Imports
import jinja2
from flask import Flask, app
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy


# ============================================================================ #
# Private methods
# ---------------------------------------------------------------------------- #
def _register_blueprint_events():
    from .private.routes import bp_private
    from .public.routes import bp_public

    def do_after_blueprint_request(r):
        # @app.teardown_request
        # def shutdown_session(exception=None):
        # It is 'usually'define in teardown_request. but is to often, each time a
        #   "GET /static/img/pages/canoa_fundo-w.jpeg HTTP/1.1" 304 -
        # it shuts the session.
        try:
            global SqlAlchemySession
            if SqlAlchemySession.dirty:
                app.logger.error(
                    f"SqlAlchemySession is dirty. Modified instances: [{SqlAlchemySession.dirty}]."
                )
            else:
                app.logger.debug(
                    f"SqlAlchemySession is shuting down {('active' if SqlAlchemySession.is_active else 'inactive')} and clean."
                )

            SqlAlchemySession.remove()
        except Exception as e:
            app.logger.error(
                f"An error occurred removing the current session [{SqlAlchemySession}]. Error [{e}]."
            )

        return r

    bp_private.after_request(do_after_blueprint_request)
    bp_public.after_request(do_after_blueprint_request)

    return


# ---------------------------------------------------------------------------- #
def _register_blueprint_routes():
    from .private.routes import bp_private
    from .public.routes import bp_public

    app.register_blueprint(bp_private)
    app.register_blueprint(bp_public)

    return


# ---------------------------------------------------------------------------- #
def _register_jinja(debugUndefined: bool, app_name: str, app_version: str):
    from .private.logged_user import logged_user
    from .helpers.route_helper import private_route, public_route, static_route

    app.jinja_env.globals.update(
        app_name=app_name,
        app_version=app_version,
        static_route=static_route,
        private_route=private_route,
        public_route=public_route,
        logged_user=logged_user,
    )

    if debugUndefined:
        # Enable DebugUndefined for better error messages in Jinja2 templates
        app.jinja_env.undefined = jinja2.DebugUndefined
    return


# ---------------------------------------------------------------------------- #
def _register_login_manager():
    from flask_login import LoginManager

    global login_manager
    login_manager = LoginManager()
    login_manager.init_app(app)

    return


# ---------------------------------------------------------------------------- #
def _register_db():

    db = SQLAlchemy()
    db.init_app(app)
    return


# ---------------------------------------------------------------------------- #
def db_obfuscate(config):
    """Hide any confidencial info before is displayed in debug mode"""
    import re

    db_uri = str(config.SQLALCHEMY_DATABASE_URI)
    db_uri_safe = re.sub(
        config.SQLALCHEMY_DATABASE_URI_REMOVE_PW_REGEX,
        config.SQLALCHEMY_DATABASE_URI_REPLACE_PW_STR,
        config.SQLALCHEMY_DATABASE_URI,
    )
    config.SQLALCHEMY_DATABASE_URI = db_uri_safe
    return db_uri


# ============================================================================ #
# App + helpers
def create_app():
    from .app_constants import app_name, app_version

    # === Check if all mandatory information is ready === #
    from .igniter import ignite_sidekick
    from .igniter import ignite_log_file

    sidekick, display_mute_after_init = ignite_sidekick(app_name, started)

    # === Global app, Create the Flask App  ===`#
    global app
    name = __name__ if __name__.find(".") < 0 else __name__.split(".")[0]
    app = Flask(name)
    sidekick.display.info(f"The Flask App was created, named '{name}'.")
    sidekick.keep(app)
    sidekick.display.info(
        f"[{sidekick}] instance is now ready. It will be cached for use between requests."
    )

    # -- app config
    app.config.from_object(sidekick.config)
    sidekick.display.info("App's config was successfully bound.")
    app.config.from_prefixed_env(app_name)
    sidekick.display.info("App's config updated with Environment Variables.")

    # -- Logfile
    if sidekick.config.LOG_TO_FILE:
        # only returns if everything went well.
        filename, level = ignite_log_file(sidekick.config, app)
        info = f"file '{filename}' levels '{level}' and above"
        sidekick.display.info(f"Logging to {info}.")
        # TODO: displayed_levels = [name for level, name in levels.items() if level >=\

        app.logger.log(sidekick.config.LOG_MIN_LEVEL, f"{app_name}'s log {info} is ready.")
        sidekick.config.LOG_FILE_STATUS = "ready"
    else:
        sidekick.config.LOG_FILE_STATUS = "off"

    # -- Register SQLAlchemy
    _register_db()
    sidekick.display.info("The app was registered in SqlAlchemy.")

    # -- Register BluePrint events & routes
    _register_blueprint_events()
    sidekick.display.info("Added 'after_request' event for all blueprints.")
    _register_blueprint_routes()
    sidekick.display.info("The blueprint routes were collected and registered within the app.")

    # -- Jinja2
    _register_jinja(sidekick.config.DEBUG_TEMPLATES, app_name, app_version)
    sidekick.display.info(
        f"The Jinja functions of this app have been attached 'jinja_env.globals' (with debug_templates {sidekick.config.DEBUG_TEMPLATES})."
    )

    # -- Jinja Login Manager
    _register_login_manager()
    sidekick.display.info("The Login Manager was initialized with the app.")

    # == Global Config, save here (__init__.py) to recreate sidekick
    global Config
    uri = db_obfuscate(sidekick.config)
    Config = sidekick.config
    sidekick.display.info("The global Config is ready.")

    # -- Connect to Database
    from .igniter import ignite_sql_connection

    ignite_sql_connection(sidekick, uri)
    sidekick.display.info("SQLAlchemy was instantiated and the db connection was successfully tested.")

    # == Global Scoped SQLAlchemy Session
    global SqlAlchemySession
    engine = create_engine(uri)
    # https://docs.sqlalchemy.org/en/20/orm/contextual.html
    # https://flask.palletsprojects.com/en/stable/patterns/sqlalchemy/
    SqlAlchemySession = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    sidekick.display.info("A scoped SQLAlchemy session was instantiated.")

    # config sidekick.display
    if display_mute_after_init:
        sidekick.display.mute_all = True

    return app, sidekick


# eof
