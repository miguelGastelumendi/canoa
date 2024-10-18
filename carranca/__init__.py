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
# cSpell:ignore sqlalchemy keepalives psycopg2

# For Display() perf display

import time
started = time.perf_counter()

import jinja2
from flask import Config
from flask_sqlalchemy import SQLAlchemy



# def _register_database(app, sa: SQLAlchemy):

#     sa.init_app(app)

#     # @app.before_first_request
#     # def initialize_database():
#     #     db.create_all()

#     """ ChatGPT
#     During each request:
#         Flask receives the request.
#         Your view logic runs, interacting with the database through app_db.
#         Once the response is ready, the shutdown_session() is called,
#         which removes the session to prevent any lingering database connections or transactions.
#     """
#     @app.teardown_request
#     def shutdown_session(exception=None):
#        sa.session.remove()


# ---------------------------------------------------------------------------- #
#from config import BaseConfig
def create_app(app_name, config: Config):
    from flask import Flask

    # alternative configuration to Flask
    app = Flask(app_name)
    app.config.from_prefixed_env(config.APP_NAME)
    app.config.from_object(config)

    #with app.app_context():
    # _register_database(app, sa)

    if config.DEBUG_TEMPLATES:
        # Enable DebugUndefined for better error messages in Jinja2 templates
        app.jinja_env.undefined = jinja2.DebugUndefined

    return app


# eof
