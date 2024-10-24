"""
  Sidekick
    Sidekick is class to keep easily accessible
    frequently used objects

    This object is initialized in package/__init__.py

        Sidekick objects:
        ├── config         config.Config + app.config (see sidekick.py header for more info)
        ├── app_log        Flask's app logger
        └── display        mgd's simple text display to console


    app.config vs config
    ------------------------
    `app.config` has almost all the attributes of the `config``
    *plus* those of Flask.

    So to keep it 'mode secure' and avoid 'circular imports',
    use sidekick.config

    app_log == app.Logger
    ---------------------

    v1 Shared mgd 2024-07-22,10-07
    v2 Sidekick 2024.10.23
"""

# cSpell:ignore sqlalchemy mgd appcontext

import json
from flask import Flask, g
from datetime import datetime
from .helpers.Display import Display
from .DynamicConfig import DynamicConfig

sidekick = None
# ---

def create_sidekick(config: DynamicConfig, display: Display):
    global sidekick
    sidekick = Sidekick(config, display)
    return sidekick


def recreate_sidekick(config: DynamicConfig, app: Flask):
    # from .helpers.Display import Display
    global sidekick

    display = Display()  # TODO: config
    sidekick = Sidekick(config, display, app)
    return sidekick


class Sidekick:
    """
    A handy hub for sidekick objects
    """

    def __init__(self, config: DynamicConfig, display: Display, app: Flask = None):
        self.debugging = config.debugging
        self.app_name = config.APP_NAME
        self.config = config
        self.display = display
        self.started_at = datetime.now()
        self.keep(app)

    def keep(self, app):
        # https://docs.python.org/3/library/logging.html
        self.app = app
        self.app_log = None if app is None else app.logger
        return

    def __repr__(self):
        return json.dumps(self.info, indent=4, sort_keys=True)


# eof
