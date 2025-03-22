"""
Package/__init__.py
`This file is executed by the Python interpreter on startup, once`

Equipe da Canoa -- 2024
mgd

"""

# cSpell:ignore app_name sqlalchemy sessionmaker autoflush gethostname connstr juser

# ============================================================================ #
from flask_login import LoginManager
from sqlalchemy.orm import scoped_session
from .common.Sidekick import Sidekick
from typing import Optional

# 4 App Global variables
global_sidekick: Optional[Sidekick] = None
global_login_manager: Optional[LoginManager] = None
global_sqlalchemy_scoped_session: Optional[scoped_session] = None
APP_DB_VERSION: str = "?"

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
            if global_sqlalchemy_scoped_session.dirty:
                app.logger.error(
                    f"SqlAlchemySession is dirty. Modified instances: [{global_sqlalchemy_scoped_session.dirty}]."
                )
            else:
                app.logger.debug(
                    f"SqlAlchemySession is shutting down {('active' if global_sqlalchemy_scoped_session.is_active else 'inactive')} and clean."
                )

            global_sqlalchemy_scoped_session.remove()
        except Exception as e:
            app.logger.error(
                f"An error occurred removing the current session [{global_sqlalchemy_scoped_session}]. Error [{e}]."
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

    def get_jinja_user() -> Optional[JinjaUser]:
        juser: JinjaUser = None
        if is_someone_logged():
            # 'import logged_user' only when a user is logged
            from .common.app_context_vars import jinja_user

            juser = jinja_user

        return juser

    app.jinja_env.globals.update(
        app_name=app_name,
        app_version=app_version,
        static_route=static_route,
        private_route=private_route,
        public_route=public_route,
        logged_user=get_jinja_user,
    )

    if debugUndefined:
        # Enable DebugUndefined for better error messages in Jinja2 templates
        app.jinja_env.undefined = jinja2.DebugUndefined
    return


# ---------------------------------------------------------------------------- #
def _do_sqlalchemy_scoped_session(uri: str) -> scoped_session:

    # https://docs.sqlalchemy.org/en/20/orm/contextual.html
    # https://flask.palletsprojects.com/en/2.3.x/patterns/sqlalchemy/

    engine = create_engine(uri, future=True)
    new_session = sessionmaker(autocommit=False, autoflush=True, bind=engine)
    uri = None

    return scoped_session(new_session)


# ---------------------------------------------------------------------------- #
def _register_db(app: Flask):

    db = SQLAlchemy()
    db.init_app(app)

    return


# ---------------------------------------------------------------------------- #
def _info(text: str):  # shortcut
    global_sidekick.display.info(text)


# ---------------------------------------------------------------------------- #
def _create_app_and_log_file(app_name: str):
    from .helpers.db_helper import db_connstr_obfuscate
    from .helpers.log_helper import do_log_file

    # -- the Flask's app
    app = Flask(app_name)
    _info(f"The Flask App was created, named '{app.name}'.")

    # -- config from file
    app.config.from_object(global_sidekick.config)
    # obfuscate after app is configured
    db_connstr_obfuscate(global_sidekick.config)
    _info("App's config was successfully bound to the app.")

    # -- config from env vars
    app.config.from_prefixed_env(app_name)
    pcName = socket.gethostname().upper()
    _info(f"App's config updated with environment variables from [{pcName}].")

    # -- Log file
    if not global_sidekick.config.LOG_TO_FILE:
        global_sidekick.config.LOG_FILE_STATUS = "off"
    else:
        cfg = global_sidekick.config
        error, full_name, level = do_log_file(
            app, cfg.LOG_FILE_NAME, cfg.LOG_FILE_FOLDER, cfg.LOG_MIN_LEVEL
        )
        if not error:
            info = f"file '{full_name}' levels '{level}' and above"
            _info(f"Logging to {info}.")
            app.logger.log(global_sidekick.config.LOG_MIN_LEVEL, f"{app.name}'s log {info} is ready.")
            global_sidekick.config.LOG_FILE_STATUS = "ready"
        else:
            global_sidekick.config.LOG_FILE_STATUS = "error"
            global_sidekick.display.error(f"{app_name}'s log {info} creation error: [{error}].")

    return app


# ============================================================================ #
# App + helpers
def create_app():
    from .common.app_constants import APP_NAME, APP_VERSION
    from .common.igniter import ignite_app

    # /!\ =================================================
    # Global variables should be assigned before any other module
    # imports them. If not, they will remain None even if a value
    # is assigned before being used.

    # === 1/3 Global sidekick  === #
    global global_sidekick, APP_DB_VERSION
    # === Check if all mandatory information is ready === #
    global_sidekick, APP_DB_VERSION, display_mute_after_init = ignite_app(APP_NAME, started)
    _info(f"[{global_sidekick}] instance is now ready. It will be available during app's context.")

    # == 2/3 Global Scoped SQLAlchemy Session
    global global_sqlalchemy_scoped_session
    db_uri = str(global_sidekick.config.SQLALCHEMY_DATABASE_URI)
    global_sqlalchemy_scoped_session = _do_sqlalchemy_scoped_session(db_uri)
    _info("A scoped SQLAlchemy session was successfully instantiated.")

    # === Flask App, config it & file log ===`#
    app = _create_app_and_log_file(APP_NAME)

    # === 3/3 Global Jinja Login Manager
    global global_login_manager
    global_login_manager = LoginManager()
    global_login_manager.init_app(app)
    _info("The Login Manager has been successfully initialized and attached to the app.")

    # -- Register SQLAlchemy
    _register_db(app)
    _info("The app was registered in SqlAlchemy.")

    # -- Register BluePrint events & routes
    _register_blueprint_events(app)
    _info("Added 'after_request' event for all blueprints.")
    _register_blueprint_routes(app)
    _info("The blueprint routes were collected and registered within the app.")

    # -- Jinja2
    _register_jinja(app, global_sidekick.config.DEBUG_TEMPLATES, APP_NAME, APP_VERSION)
    _info(
        f"The Jinja functions of this app have been attached to 'jinja_env.globals' (with debug_templates {global_sidekick.config.DEBUG_TEMPLATES})."
    )

    # config sidekick.display
    if display_mute_after_init:
        global_sidekick.display.mute_all = True

    return app, global_sidekick


# eof
