"""
  Shared
    Shared is class to keep easily accessible frequently
    shared objects

    This object is initialized in package/__init__.py

        Shared shared objects:
        ├── config         config.Config + app.config (see Shared.py header for more info)
        ├── sa             SqlAlchemy
        ├── sa_engine      SqlAlchemy engine
        ├── login_manager  Flask's login manager
        ├── app_log        Flask's app logger
        └── display        mgd's simple text display to console



    app.config vs config
    ------------------------
    `app.config` has almost all the attributes of the `config``
    *plus* those of Flask.

    So to keep it 'mode secure' and avoid 'circular imports',
    use shared.config

    app_log == app.Logger
    ---------------------

    mgd 2024-07-22,10-07
"""

# cSpell:ignore sqlalchemy mgd sessionmaker

import json
from datetime import datetime
from flask import Config

from .helpers.py_helper import copy_attributes


class Shared:
    """
    A global hub for shared objects
    """

    from .Config import DynamicConfig
    from .helpers.Display import Display

    def __init__(self, app_debug: bool, config: DynamicConfig, display: Display, server_address: str):
        self.app_log = None
        self.app_name = config.APP_NAME
        self.app_debug = app_debug
        self.config = config
        self.display = display
        self.login_manager = None
        self.sa = None
        self.sa_engine = None
        self.server_address = server_address
        self.started_at = datetime.now()

    def keep(self, app, sa, login_manager):
        # https://docs.python.org/3/library/logging.html
        self.app_log = app.logger
        self.sa = sa
        self.sa_engine = sa.get_engine(app)

        ## TODO login_manager.login_view = 'auth.login'
        login_manager.init_app(app)
        self.login_manager = login_manager

        return self

    info = {
        "app_log": "Flask's app logger",
        "config": "config.Config",
        "display": "mgd's simple text display to console",
        "login_manager": "Flask's login manager",
        "sa": "SqlAlchemy",
        "sa_engine": "SqlAlchemy engine",
    }

    def obfuscate(self):
        """ Hide any confidencial info before is displayed in debug mode"""
        import re

        db_uri_safe = re.sub(
            self.config.SQLALCHEMY_DATABASE_URI_REMOVE_PW_REGEX,
            self.config.SQLALCHEMY_DATABASE_URI_REPLACE_PW_STR,
            self.config.SQLALCHEMY_DATABASE_URI,
        )
        self.config.SQLALCHEMY_DATABASE_URI = db_uri_safe

    def __repr__(self):
        return json.dumps(self.info, indent=4, sort_keys=True)


# eof
