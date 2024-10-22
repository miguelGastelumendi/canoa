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
        │    ├── shared.py     # shared var with most used object (app, config, sa, etc)
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
from flask import Flask
from sqlalchemy import create_engine
from flask_login import LoginManager
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy


# ============================================================================ #
# Public variables
db = SQLAlchemy()
login_manager = LoginManager()
Session = None


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

    def __get_name() -> str:
        return app.config["APP_NAME"]

    def __get_version() -> str:
        return app.config["APP_VERSION"]

    app.jinja_env.globals.update(
        app_version=__get_version,
        app_name=__get_name,
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
        Session.remove()


# ============================================================================ #
# App + helpers
def create_app(app_name):

    # === Create the Flask lApp  ===`#
    app = Flask(app_name, static_folder="static", instance_relative_config=True)

    # === Check if all mandatory information is ready === #
    from .igniter import ignite_shared

    shared, display_mute_after_init = ignite_shared(app_name, started)
    shared.display.info("The Flask App was created.")

    # -- Configuration
    app.config.from_prefixed_env(app_name)
    app.config.from_object(shared.config)
    shared.display.info("App's config was successfully bound.")

    # -- Register modules
    _register_db(app)
    shared.display.info("The db was registered.")
    _register_blueprints(app)
    shared.display.info("The blueprints were collected and registered within the app.")
    _register_jinja(app, shared.config.DEBUG_TEMPLATES)
    shared.display.info("This app's functions were registered into Jinja.")
    _register_login_manager(app)
    shared.display.info("The Login Manager was initialized with the app.")

    # -- Database
    from .igniter import ignite_sql_connection

    uri = shared.db_obfuscate()
    ignite_sql_connection(shared, uri)
    shared.display.info("SQLAlchemy was instantiated and the db connection was successfully tested.")

    # -- Database
    global Session
    engine = create_engine(uri)
    Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    # config shared.display
    if display_mute_after_init:
        shared.display.mute_all = True

    return app


# eof
