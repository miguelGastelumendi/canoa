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


class Shared:
    def __init__(self, config, display, server_address):
        self.app_log = None
        self.config = config
        self.display = display
        self.login_manager = None
        self.sa = None
        self.sa_engine = None
        self.server_address = server_address
        self.started_at = datetime.now()
        self.cache = None # TODO: _get_form_data

    def keep(self, app, sa, login_manager):
        self.app_log = app.logger
        self.sa = sa
        self.sa_engine = sa.get_engine(app)

        ## TODO login_manager.login_view = 'auth.login'
        login_manager.init_app(app)
        self.login_manager = login_manager

        return self

    def doSession(self):
        from sqlalchemy.orm import sessionmaker

        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#using-a-sessionmaker
        Session = sessionmaker(bind=self.sa_engine)
        session = Session()
        return session

    info = {
        "app_log": "Flask's app logger",
        "config": "config.Config",
        "display": "mgd's simple text display to console",
        "login_manager": "Flask's login manager",
        "sa": "SqlAlchemy",
        "sa_engine": "SqlAlchemy engine",
    }

    def __repr__(self):
        return json.dumps(self.info, indent=4, sort_keys=True)


# eof
