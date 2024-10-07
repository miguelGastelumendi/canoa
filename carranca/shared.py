"""
 #Shared
    Shared is class to easily share frequently
    used app's properties & other useful objects

    This object is initialized in package/__init__.py

    app.config vs app_config
    ------------------------
    `app.config` has all the attributes of the `app_config``
    *plus* those of Flask.

    So to keep it 'mode secure' and avoid 'circular imports',
    import just `app_config` instead of `app` to use app.config

    app_log == app.Logger
    ---------------------

    mgd 2024-07-22
"""

# cSpell:ignore sqlalchemy keepalives

from datetime import datetime
from copy import copy as copy_str


class Shared:
    def __init__(self):
        self.app_config = None
        self.app_log = None
        self.db = None
        self.db_engine = None
        self.login_manager = None
        self.started_at = datetime.now()

    def _create_engine(self) -> any:
        from sqlalchemy import create_engine

        result = create_engine(
            copy_str(self.app_config.SQLALCHEMY_DATABASE_URI),
            isolation_level="AUTOCOMMIT",  # "READ UNCOMMITTED", # mgd em Canoa, acho desnecessário
            pool_pre_ping=True,
            connect_args={
                # (https://www.postgresql.org/docs/current/libpq-connect.html)
                # Maximum time to wait while connecting, in seconds  was 600.
                # instead mhd is using `pool_pre_ping` and set connect_timeout to 10
                "connect_timeout": 10,
                "application_name": self.app_config.APP_NAME,
                "keepalives": 1,
            },
        )
        # not need any more.
        self.app_config.SQLALCHEMY_DATABASE_URI = None
        return result

    def initialize(self, app_config, display):
        self.app_config = app_config
        self.display = display

        from flask_sqlalchemy import SQLAlchemy

        self.db = SQLAlchemy()
        self.db_engine = self._create_engine()

        from flask_login import LoginManager

        self.login_manager = LoginManager()


# eof
