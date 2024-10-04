"""
    The main script ;-)

    For newbies, remember:
       Canoa/
        ├── __init__.py     # Crucial empty file (tells Python that tis folder is a package (Canoa)
        ├── main.py         # <- You are here
        ├── App/            # Optional folder for application logic
        │    ├── shared.py  # shared vars
        │    ├── config.py  # configuration file
        │    ├── config_..  # config_validate_process.py specific configurations for the validate process
        │    └── ...        # Other files in the App folder
        └── other_files.py  # Other Python files in the root directory

    see https://flask.palletsprojects.com/en/latest/tutorial/factory/


    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore sqlalchemy, cssless sendgrid, ENDC

import re
import time

started = time.perf_counter()

from sys import exit
from collections import namedtuple
from flask_minify import Minify
from urllib.parse import urlparse

from carranca.helpers.Display import Display as Display
from carranca.helpers.py_helper import is_str_none_or_empty
from carranca.config import (
    config_modes,
    BaseConfig,
    app_mode_production,
    app_mode_debug,
)


# ---------------------------------------------------------------------------- #
# Helpers
def _display(msg):
    Display.error(msg, f"{BaseConfig.APP_NAME}: ")

def __log_and_exit(ups: str):
    _display(ups)
    exit(ups)

def __is_empty(key: str) -> bool:
    value = getattr(_app_config, key, "")
    empty = value is None or value.strip() == ""
    if empty:
        _display(f"Key [{key}] has no value.")
    return empty


# ---------------------------------------------------------------------------- #
# Select the _app_config, based in the app_mode (production or debug)
# WARNING: Don't run with debug turned on in production!
_app_mode = ""
_app_config = None

try:
    _app_mode = BaseConfig.get_os_env("APP_MODE", app_mode_debug)
    _app_config = config_modes[_app_mode]
except KeyError:
    __log_and_exit(
        f"Error: Invalid <app_mode>: '{_app_mode}'. Expected values are [{app_mode_debug}, {app_mode_production}]."
    )

# ---------------------------------------------------------------------------- #
# Hi password from Connection String
_db_uri_key = "SQLALCHEMY_DATABASE_URI"
_db_uri_safe = re.sub(
    _app_config.SQLALCHEMY_DATABASE_URI_REMOVE_PW_REGEX,
    ":******@",
    getattr(_app_config, _db_uri_key),
)

# ---------------------------------------------------------------------------- #
# Check if the mandatory environment variables are set.
if __is_empty(_db_uri_key) or __is_empty("SERVER_ADDRESS") or __is_empty("SECRET_KEY"):
    __log_and_exit("One or more mandatory environment variables were not set.")

# ---------------------------------------------------------------------------- #
# Confirm we have a well formed http address
Address = namedtuple("Address", "host, port")
address = Address("", 0)
try:
    default_scheme = "http://"
    url = urlparse(_app_config.SERVER_ADDRESS, default_scheme, False)
    # there is a bug is Linux (?) url.hostname  & url.port are always None
    path = ["", ""] if is_str_none_or_empty(url.path) else f"{url.path}:".split(":")
    address = Address(
        path[0] if is_str_none_or_empty(url.hostname) else url.hostname,
        path[1] if is_str_none_or_empty(url.port) else url.port,
    )
except Exception as e:
    _display(
        f"`urlparse('{_app_config.SERVER_ADDRESS}', '{default_scheme}') -> parsed: {address.host}:{address.port}`",
    )
    __log_and_exit(
        f"Error parsing server address. Expect value is [HostName:Port], found: [{_app_config.SERVER_ADDRESS}]. Error {e}"
    )

# ---------------------------------------------------------------------------- #
# Ready to create App
# ---------------------------------------------------------------------------- #
# Create th Flask's app and update the very common shared objects in shared.py
from __init__1 import create_app

app = create_app(_app_config)
setattr(_app_config, _db_uri_key, _db_uri_safe)

# ---------------------------------------------------------------------------- #
# Minified html/js when requested or not in Debug
_app_config.APP_MINIFIED = (
    _app_config.APP_MINIFIED if _app_config.APP_MINIFIED else not _app_config.DEBUG
)
if _app_config.APP_MINIFIED:
    Minify(app=app, html=True, js=True, cssless=False)

# ---------------------------------------------------------------------------- #
# Log initial configuration
# TODO Argument --info
Display.info(
    f"{_app_config.APP_NAME} Version {_app_config.APP_VERSION} started in {_app_config.APP_MODE} in mode :-)."
)
if _app_config.DEBUG: # or to_str(args[1]):
    from carranca.public.debug_info import get_debug_info
    get_debug_info(True)

# ---------------------------------------------------------------------------- #
# Give warnings of import configuration that may be missing
if is_str_none_or_empty(_app_config.EMAIL_API_KEY):
    app.logger.warning(
        f"Sendgrid API key was not found, the app will not be able to send emails."
    )

if is_str_none_or_empty(_app_config.EMAIL_ORIGINATOR):
    app.logger.warning(
        f"The app email originator is not defined, the app will not be able to send emails."
    )

if is_str_none_or_empty(address.host) or (address.port == 0):
    __log_and_exit(
        f"Invalid hot or port address, found [{_app_config.SERVER_ADDRESS}], parsed: {address.host}:{address.port}`"
    )

# ---------------------------------------------------------------------------- #
# Ready to go, lunch!
if __name__ == "__main__":
    elapsed = (time.perf_counter() - started) * 1000
    Display.info(f"{__name__} ready in {elapsed:,.0f}ms")
    Display.info(f"Launching {_app_config.APP_NAME} v {_app_config.APP_VERSION}")
    app.run(host=address.host, port=address.port, debug=_app_config.DEBUG)
else:
    __log_and_exit(f"Expected '__main__' as __name__, but got '{__name__}' instead. Exiting...")

# eof
