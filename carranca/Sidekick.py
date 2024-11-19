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
from flask import Flask
from datetime import datetime

from .helpers.py_helper import get_init_params
from .helpers.Display import Display
from .DynamicConfig import DynamicConfig

# Global
sidekick = None
display_params = "DISPLAY_PARAMS"
# ------


def create_sidekick(config: DynamicConfig, display: Display):
    global sidekick
    config[display_params] = get_init_params(display)
    sidekick = Sidekick(config, display)
    return sidekick


def recreate_sidekick(config: DynamicConfig, app: Flask):
    # from .helpers.Display import Display
    global sidekick

    msg_error = None
    try:
        _params = config[display_params]
        display = Display(**_params)
    except Exception as e:
        display = Display()  # use default
        msg_error = str(e)

    sidekick = Sidekick(config, display, app)
    sidekick.display.info("Sidekick was recreated.")
    if msg_error:
        sidekick.display.error(f"But using default params: {msg_error}.")

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

    # def __repr__(self):
    #     return json.dumps(self.config__dict__, indent=4, sort_keys=True)


# eof
