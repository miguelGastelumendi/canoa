# Package/__init__.py
# This file, is execute by the Python interpreter on startup once

"""
    The main script ;-)

    For newbies, remember:
       Canoa/
        ├── LocalDrive         # git ignored folder for project dev info
        ├── user_files         # git ignored folder with all the users files downloaded for validation
        ├── carranca/          # main application package
        |    ├── __init__.py   # crucial (tells Python that tis folder is a package (carranca). Creates the app
        │    ├── main.py       # <- You are here
        │    ├── sidekick.py     # shared var with most used object (app, config, sa, etc)
        │    ├── config.py     # configuration file
        │    ├── config_..     # config_validate_process.py specific configurations for the validate process
        │    ├── helpers
        |    |    ├──:        # py files
        │    ├── private
        |    |    ├──:         # models, routes, forms py files
        |    |    ├── access_control
        |    |    |   └── password_change
        |    |    └── validate_process
        |    |         └──:     # py files required for the validation process
        │    ├── public
        |    |    ├──:          # models, routes, forms, etc py files
        |    |    └── access_control
        |    |         └──:     # login, password_recovery, password_reset, register
        │    ├── static         # assets, css, docs, img, js
        │    └── templates      # jinja templates
        |         ├── accounts
        |         ├── home
        |         ├── includes
        |         ├── layouts
        |         └── private
        |
        ├── requirements.txt
        ├── README.md
        ├── .gitignore
        ├── mgd-logbook.txt my log file
        ├─: several bat/sh for to start data_validate
        ├─: IIS (MS Internet Information Services) configuration files *web.config
        └─: .env .git .vscode


    see https://flask.palletsprojects.com/en/latest/tutorial/factory/


    Equipe da Canoa -- 2024
    mgd
"""
# cSpell:ignore app_name sqlalchemy sessionmaker autoflush

import time

started = time.perf_counter()

import jinja2
from flask import Flask, g
from sqlalchemy import create_engine
from flask_login import LoginManager
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy


# ============================================================================ #
# Public variables
db = SQLAlchemy()
login_manager = LoginManager()
Session = None
Config = None


# ============================================================================ #
# Private methods
# ---------------------------------------------------------------------------- #
def _register_blueprints(app):
    from .private.routes import bp_private
    from .public.routes import bp_public

    app.register_blueprint(bp_private)
    app.register_blueprint(bp_public)
    return


# ---------------------------------------------------------------------------- #
def _register_jinja(app, debugUndefined):
    from .helpers.route_helper import private_route, public_route
    from .helpers.pw_helper import is_someone_logged

    def __get_name() -> str:
        return app.config["APP_NAME"]

    def __get_version() -> str:
        return app.config["APP_VERSION"]

    def __user_is_logged() -> bool:
        return is_someone_logged()

    app.jinja_env.globals.update(
        app_version=__get_version,
        app_name=__get_name,
        user_logged=__user_is_logged,
        private_route=private_route,
        public_route=public_route,
    )

    if debugUndefined:
        # Enable DebugUndefined for better error messages in Jinja2 templates
        app.jinja_env.undefined = jinja2.DebugUndefined
    return


# ---------------------------------------------------------------------------- #
def _register_login_manager(app):

    login_manager.init_app(app)
    return


# ---------------------------------------------------------------------------- #
def _register_db(app):

    db.init_app(app)
    # @app.before_first_request
    # def initialize_database():
    #     db.create_all()

    """ ChatGPT
    During each request:
        Flask receives the request.
        Your view logic runs, interacting with the database through app_db.
        Once the response is ready, the shutdown_session() is called,
        which removes the session to prevent any lingering database connections or transactions.
    """

    @app.teardown_request
    def shutdown_session(exception=None):
        try:
            Session.remove()
        except Exception as e:
            if app:
                app.logger.error(f"An error ocurred removing the current session [{Session}]. Error [{e}].")


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
def create_app(app_name: str):

    # === Check if all mandatory information is ready === #
    from .igniter import ignite_sidekick
    from .igniter import ignite_log_file

    sidekick, display_mute_after_init = ignite_sidekick(app_name, started)

    # === Create the Flask App  ===`#
    name = __name__ if __name__.find(".") < 0 else __name__.split(".")[0]
    app = Flask(name)
    sidekick.display.info(f"The Flask App was created, named '{name}'.")

    # -- app config
    from .helpers.py_helper import copy_attributes

    # _config = copy_attributes(sidekick.config)  # only attributes needed
    app.config.from_object(sidekick.config)
    app.config.from_prefixed_env(app_name)
    sidekick.display.info("App's config was successfully bound.")

    # -- Logfile
    if sidekick.config.LOG_TO_FILE:
        filename, level = ignite_log_file(sidekick.config, app)
        info = f"file '{filename}' with level {level}"
        sidekick.display.info(f"Logging to {info}.")
        app.logger.log(sidekick.config.LOG_FILE_LEVEL, f"{sidekick.config.APP_NAME}'s log {info} is ready.")
        sidekick.config.LOG_FILE_STATUS = "ready"
    else:
        sidekick.config.LOG_FILE_STATUS = "off"

    # -- Register modules
    _register_db(app)
    sidekick.display.info("The db was registered.")

    _register_blueprints(app)
    sidekick.display.info("The blueprints were collected and registered within the app.")

    _register_jinja(app, sidekick.config.DEBUG_TEMPLATES)
    sidekick.display.info(
        f"This app's functions were registered into Jinja (with debug_templates {sidekick.config.DEBUG_TEMPLATES})."
    )

    _register_login_manager(app)
    sidekick.display.info("The Login Manager was initialized with the app.")

    # == Config
    global Config
    uri = db_obfuscate(sidekick.config)
    Config = sidekick.config

    # -- Connect to Database
    from .igniter import ignite_sql_connection

    ignite_sql_connection(sidekick, uri)
    sidekick.display.info("SQLAlchemy was instantiated and the db connection was successfully tested.")

    # == Database Session
    global Session
    engine = create_engine(uri)
    Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    sidekick.display.info("A sharable scoped SQLAlchemy session was instantiated.")

    # config sidekick.display
    if display_mute_after_init:
        sidekick.display.mute_all = True

    @app.before_request
    def do_before_request():
        # TODO
        # if "sidekick" not in g:
        #     from .Sidekick import recreate_sidekick
        #     g.sidekick = recreate_sidekick(Config, app_name)

        from .Sidekick import recreate_sidekick

        sidekick = recreate_sidekick(Config, app)

    # run parameters host & port are taken from SERVER_NAME
    # https://flask.palletsprojects.com/en/3.0.x/api/#flask.Flask.run

    return app


# eof
