"""
Package/__init__.py
`This file is executed by the Python interpreter on startup, once`

Equipe da Canoa -- 2024
mgd

"""

# cSpell:ignore app_name sqlalchemy sessionmaker autoflush gethostname

# ============================================================================ #
from flask_login import LoginManager
from sqlalchemy.orm import scoped_session
from .common.Sidekick import Sidekick

# Public/Global variables
global_sidekick: Sidekick = None
global_login_manager: LoginManager = None
SqlAlchemyScopedSession: scoped_session = None

"""
'scoped' refers to the management of SQLAlchemy `Session` objects within a specific scope,
such as a thread or a request in a web application. The `scoped_session` class provides
a way to ensure that each thread or request gets its own session, which is isolated from
sessions used by other threads or requests.

The main advantage of using `scoped_session` is that it simplifies session management in
multi-threaded or multi-request environments by automatically handling the creation
and removal of sessions based on the current scope.
"""

# Module variable
import time

started = time.perf_counter()

# Imports
import jinja2
import socket
from flask import Flask
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

from .private.JinjaUser import JinjaUser
from .helpers.pw_helper import is_someone_logged
from .helpers.route_helper import private_route, public_route, static_route


# ============================================================================ #
# Private methods
# ---------------------------------------------------------------------------- #
def _register_blueprint_events(app: Flask):
    from .private.routes import bp_private
    from .public.routes import bp_public

    def do_after_blueprint_request(r):
        # @app.teardown_request
        # def shutdown_session(exception=None):
        # It is 'usually'define in teardown_request. but is to often, each time a
        #   "GET /static/img/pages/canoa_fundo-w.jpeg HTTP/1.1" 304 -
        # it shuts the session.
        try:
            global SqlAlchemyScopedSession
            if SqlAlchemyScopedSession.dirty:
                app.logger.error(
                    f"SqlAlchemySession is dirty. Modified instances: [{SqlAlchemyScopedSession.dirty}]."
                )
            else:
                app.logger.debug(
                    f"SqlAlchemySession is shutting down {('active' if SqlAlchemyScopedSession.is_active else 'inactive')} and clean."
                )

            SqlAlchemyScopedSession.remove()
        except Exception as e:
            app.logger.error(
                f"An error occurred removing the current session [{SqlAlchemyScopedSession}]. Error [{e}]."
            )

        return r

    bp_private.after_request(do_after_blueprint_request)
    bp_public.after_request(do_after_blueprint_request)

    return


# ---------------------------------------------------------------------------- #
def _register_blueprint_routes(app: Flask):
    from .private.routes import bp_private
    from .public.routes import bp_public

    app.register_blueprint(bp_private)
    app.register_blueprint(bp_public)

    return


# ---------------------------------------------------------------------------- #
def _register_jinja(app: Flask, debugUndefined: bool, app_name: str, app_version: str):

    def get_logged_user() -> Optional[JinjaUser]:
        user: JinjaUser = None
        if is_someone_logged():
            # import here only when a user is logged
            from .common.app_context_vars import logged_user

            user = JinjaUser(logged_user)

        return user

    app.jinja_env.globals.update(
        app_name=app_name,
        app_version=app_version,
        static_route=static_route,
        private_route=private_route,
        public_route=public_route,
        logged_user=get_logged_user,
    )

    if debugUndefined:
        # Enable DebugUndefined for better error messages in Jinja2 templates
        app.jinja_env.undefined = jinja2.DebugUndefined
    return


# ---------------------------------------------------------------------------- #
def _register_login_manager(app: Flask):

    global global_login_manager
    global_login_manager = LoginManager()
    global_login_manager.init_app(app)

    return


# ---------------------------------------------------------------------------- #
def _register_db(app: Flask):

    db = SQLAlchemy()
    db.init_app(app)
    return


# ---------------------------------------------------------------------------- #
def db_obfuscate(config):
    """Hide any confidential info before it is displayed in debug mode"""
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
    from .common.app_constants import APP_NAME, APP_VERSION

    # === Check if all mandatory information is ready === #
    from .common.igniter import ignite_sidekick
    from .common.igniter import ignite_log_file

    # === Global sidekick  === #
    global global_sidekick
    global_sidekick, display_mute_after_init = ignite_sidekick(APP_NAME, started)

    # === Global app, Create the Flask App  ===`#
    name = __name__ if __name__.find(".") < 0 else __name__.split(".")[0]
    app = Flask(name)
    global_sidekick.display.info(f"The Flask App was created, named '{name}'.")
    global_sidekick.display.info(
        f"[{global_sidekick}] instance is now ready. It will be available during app context."
    )

    # -- app config
    app.config.from_object(global_sidekick.config)
    global_sidekick.display.info("App's config was successfully bound.")
    app.config.from_prefixed_env(APP_NAME)
    pcName = socket.gethostname().upper()
    global_sidekick.display.info(f"App's config updated with environment variables from [{pcName}].")

    # -- Logfile
    if global_sidekick.config.LOG_TO_FILE:
        # only returns if everything went well.
        filename, level = ignite_log_file(global_sidekick.config, app)
        info = f"file '{filename}' levels '{level}' and above"
        global_sidekick.display.info(f"Logging to {info}.")
        # TODO: displayed_levels = [name for level, name in levels.items() if level >=\

        app.logger.log(global_sidekick.config.LOG_MIN_LEVEL, f"{APP_NAME}'s log {info} is ready.")
        global_sidekick.config.LOG_FILE_STATUS = "ready"
    else:
        global_sidekick.config.LOG_FILE_STATUS = "off"

    # -- Register SQLAlchemy
    _register_db(app)
    global_sidekick.display.info("The app was registered in SqlAlchemy.")

    # -- Jinja Login Manager
    _register_login_manager(app)
    global_sidekick.display.info("The Login Manager was initialized with the app.")

    # -- Register BluePrint events & routes
    _register_blueprint_events(app)
    global_sidekick.display.info("Added 'after_request' event for all blueprints.")
    _register_blueprint_routes(app)
    global_sidekick.display.info("The blueprint routes were collected and registered within the app.")

    # -- Jinja2
    _register_jinja(app, global_sidekick.config.DEBUG_TEMPLATES, APP_NAME, APP_VERSION)
    global_sidekick.display.info(
        f"The Jinja functions of this app have been attached 'jinja_env.globals' (with debug_templates {global_sidekick.config.DEBUG_TEMPLATES})."
    )

    # -- Connect to Database
    from .common.igniter import ignite_sql_connection

    uri = db_obfuscate(global_sidekick.config)
    ignite_sql_connection(global_sidekick, uri)
    global_sidekick.display.info(
        "SQLAlchemy was instantiated and the db connection was successfully tested."
    )

    # == Global Scoped SQLAlchemy Session
    global SqlAlchemyScopedSession
    engine = create_engine(uri, future=True)
    # https://docs.sqlalchemy.org/en/20/orm/contextual.html
    # https://flask.palletsprojects.com/en/2.3.x/patterns/sqlalchemy/
    SqlAlchemyScopedSession = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
    global_sidekick.display.info("A scoped SQLAlchemy session was instantiated.")

    # config sidekick.display
    if display_mute_after_init:
        global_sidekick.display.mute_all = True

    return app, global_sidekick


# eof
