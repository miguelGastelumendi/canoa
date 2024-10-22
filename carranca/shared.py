"""
  Shared
    Shared is class to keep easily accessible frequently
    shared objects

    This object is initialized in package/__init__.py

        Shared shared objects:
        ├── config         config.Config + app.config (see Shared.py header for more info)
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

# cSpell:ignore sqlalchemy mgd appcontext

import json
from datetime import datetime

# Session variable
shared = None

def create_shared(app_debug: bool, config, display):
    global shared
    shared= Shared(app_debug,config, display)
    return shared


class Shared:
    """
    A global hub for shared objects
    """

    from .DynamicConfig import DynamicConfig
    from .helpers.Display import Display

    def __init__(self, app_debug: bool, config: DynamicConfig, display: Display):
        self.app = None
        self.app_log = None
        self.app_name = config.APP_NAME
        self.config = config
        self.uri = str(config.SQLALCHEMY_DATABASE_URI)
        self.app_debug = app_debug
        self.display = display
        self.started_at = datetime.now()

    def keep(self, app):
        # https://docs.python.org/3/library/logging.html
        self.app = app
        self.app_log = app.logger
        return

    def db_obfuscate(self):
        """Hide any confidencial info before is displayed in debug mode"""
        import re

        db_uri = self.config.SQLALCHEMY_DATABASE_URI
        db_uri_safe = re.sub(
            self.config.SQLALCHEMY_DATABASE_URI_REMOVE_PW_REGEX,
            self.config.SQLALCHEMY_DATABASE_URI_REPLACE_PW_STR,
            self.config.SQLALCHEMY_DATABASE_URI,
        )
        self.config.SQLALCHEMY_DATABASE_URI = db_uri_safe
        return db_uri

    def __repr__(self):
        return json.dumps(self.info, indent=4, sort_keys=True)


# @app.before_request
# def reignite_shared():

#     from .helpers.Display import Display
#     display = Display()


# eof
