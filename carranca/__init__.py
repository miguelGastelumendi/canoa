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
        │    ├── shared.py     # shared var with most used object (app, app_config, db, etc)
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
        |    |         └──:     # password_reset, login, reset, password_recovery
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

import time

started = time.perf_counter()
app_name = "Canoa"

# ---------------------------------------------------------------------------- #
def create_app():
    from .igniter import create_shared

    shared = create_shared(app_name, started)

    from flask import Flask

    app = Flask(app_name)
    shared.app_log = app.logger

    app.shared = shared
    app.config.from_object(shared.app_config)

    elapsed = (time.perf_counter() - started) * 1000
    shared.display.info(f"The app was created in {elapsed:,.0f}ms")
    return app


# eof
