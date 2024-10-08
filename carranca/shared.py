"""
  Shared
    Shared is class to keep easily accessible frequently
    shared objects

    This object is initialized in package/__init__.py

        Shared shared objects:
        ├── app_config     config.Config + app_config (see Shared.py header for more info)
        ├── sa             SqlAlchemy
        ├── sa_engine      SqlAlchemy engine
        ├── login_manager  Flask's login manager
        ├── app_log        Flask's app logger
        └── display        mgd's simple text display to console



    app.config vs app_config
    ------------------------
    `app.config` has all the attributes of the `app_config``
    *plus* those of Flask.

    So to keep it 'mode secure' and avoid 'circular imports',
    import just `app_config` instead of `app` to use app.config

    app_log == app.Logger
    ---------------------

    mgd 2024-07-22,10-07
"""

# cSpell:ignore sqlalchemy mgd

import json
from datetime import datetime


class Shared:
    def __init__(self, app_config, display, server_address):
        self.app_config = app_config
        self.app_log = None
        self.display = display
        self.login_manager = None
        self.sa = None
        self.sa_engine = None
        self.server_address = server_address
        self.started_at = datetime.now()

    def keep(self, app, sa, login_manager):
        import re

        db_uri_safe = re.sub(
            self.app_config.SQLALCHEMY_DATABASE_URI_REMOVE_PW_REGEX,
            self.app_config.SQLALCHEMY_DATABASE_URI_REPLACE_PW_STR,
            self.app_config.SQLALCHEMY_DATABASE_URI,
        )

        self.app_log = app.logger
        self.sa = sa
        self.sa_engine = sa.get_engine(app)

        ## TODO login_manager.login_view = 'auth.login'
        login_manager.init_app(app)
        self.login_manager = login_manager
        self.app_config.SQLALCHEMY_DATABASE_URI = db_uri_safe

        return self

    info = {
        "app_config": "config.Config + app_config",
        "app_log": "Flask's app logger",
        "display": "mgd's simple text display to console",
        "login_manager": "Flask's login manager",
        "sa": "SqlAlchemy",
        "sa_engine": "SqlAlchemy engine",
    }

    def __repr__(self):
        return json.dumps(self.info, indent=4, sort_keys=True)


# eof
