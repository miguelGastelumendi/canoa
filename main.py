"""
    The main script ;-)

    For newbies, remember:
        project_root/
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

# cSpell:ignore SQLALCHEMY, cssless sendgrid

from sys import exit
from collections import namedtuple
from flask_minify import Minify
from urllib.parse import urlparse

from carranca.config import (
    config_modes,
    BaseConfig,
    app_mode_production,
    app_mode_debug,
)
from carranca.helpers.py_helper import is_str_none_or_empty, coalesce


# ---------------------------------------------------------------------------- #
# Select the _app_config, based in the app_mode (production or debug)
# WARNING: Don't run with debug turned on in production!
_app_mode = ""
_app_config = None

try:
    _app_mode = BaseConfig.get_os_env("APP_MODE", app_mode_debug)
    _app_config = config_modes[_app_mode]
except KeyError:
    exit(
        f"Error: Invalid <app_mode>: '{_app_mode}'. Expected values are [{app_mode_debug}, {app_mode_production}]."
    )

# ---------------------------------------------------------------------------- #
# Create th Flask's app and update the very common shared objects in shared.py
from carranca import create_app
from carranca.shared import update_shared_objects
app = create_app()
update_shared_objects(app, _app_config)


# ---------------------------------------------------------------------------- #
# Helpers
def __log_and_exit(ups: str):
    app.logger.error(ups)
    exit(ups)

def __is_empty(key: str) -> bool:
    value = getattr(_app_config, key, "")
    empty = value is None or value.strip() == ""
    if empty:
        app.logger.error(f"Key [{key}] has no value.")
    return empty

# ---------------------------------------------------------------------------- #
# Check if the mandatory environment variables are set.
if (
    __is_empty("SQLALCHEMY_DATABASE_URI")
    or __is_empty("SERVER_ADDRESS")
    or __is_empty("SECRET_KEY")
):
    __log_and_exit("Mandatory environment variables were not set.")

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
    app.logger.error(
        f"`urlparse('{_app_config.SERVER_ADDRESS}', '{default_scheme}') -> parsed: {address.host}:{address.port}`"
    )
    __log_and_exit(
        f"Error parsing server address. Expect value is [HostName:Port], found: [{_app_config.SERVER_ADDRESS}]. Error {e}"
    )

# ---------------------------------------------------------------------------- #
# Minified html/js if in production
minified = False
if not _app_config.DEBUG:
    Minify(app=app, html=True, js=True, cssless=False)
    minified = True


# ---------------------------------------------------------------------------- #
# Log initial configuration
# TODO Argument --info
app.logger.info("--------------------")
app.logger.info(f"{_app_config.APP_NAME} Version {_app_config.APP_VERSION} started in {_app_config.APP_MODE} in mode :-).")
if _app_config.DEBUG:
    app.logger.info(f"Version          : {_app_config.APP_VERSION}")
    app.logger.info(f"DEBUG            : {_app_config.DEBUG}")
    app.logger.info(f"Page Compression : {minified}")
    app.logger.info(f"App root folder  : {_app_config.ROOT_FOLDER}")
    app.logger.info(f"Database address : {_app_config.SQLALCHEMY_DATABASE_URI}")
    app.logger.info(f"Server address   : {address.host}:{address.port}")
    app.logger.info(
        f"External address : {coalesce(_app_config.SERVER_EXTERNAL_IP, '<set on demand>')}"
    )
    app.logger.info(
        f"External port    : {coalesce(_app_config.SERVER_EXTERNAL_PORT, '<none>')}"
    )
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
    app.run(host=address.host, port=address.port, debug=_app_config.DEBUG)

# eof
