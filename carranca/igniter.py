"""
#igniter.py
   Common classes initializer and
   basic configuration validator module

   Equipe da Canoa -- 2024
   mgd 2024-10-01--07
"""

# cSpell:ignore sqlalchemy mandatories cssless sendgrid ENDC psycopg2

from typing import Tuple
from .helpers.py_helper import is_str_none_or_empty

_error_ = "[{0}]: An error ocurred while {1}. Message `{2}`."
fuse = None


# ---------------------------------------------------------------------------- #
# Escape Door
def _log_and_exit(ups: str):
    if fuse and fuse.display:
        fuse.display.error(ups)
    exit(ups)


# ---------------------------------------------------------------------------- #
def _start_fuse(app_name: str, started_from: float) -> Tuple[any, str]:
    """
    Create the 'fuse' that will ignite all the initializations classes
    """
    msg_error = None
    fuse = None
    try:
        from os import environ
        from .Args import Args
        from .BaseConfig import app_mode_production, app_mode_development
        from .helpers.Display import Display
        from .helpers.py_helper import set_flags_from_argv

        class Fuse:
            envvars_prefix = f"{app_name.upper()}_"

            # maybe is necessary later:
            def get_os_env(key: str, default=None) -> str:
                _key = f"{Fuse.envvars_prefix}{key}"
                return environ.get(_key, default)

            def __init__(self, app_name, debug_2):
                _args = Args(debug_2)
                self.args = set_flags_from_argv(_args)
                self.args.app_mode = None  # TODO, Test
                self.app_name = app_name
                self.app_debug = self.args.app_debug if is_str_none_or_empty(self.args.app_mode) else None
                self.app_mode = None  # TODO self.args.app_mode
                self.display = Display(
                    f"{self.app_name}: ",
                    _args.display_mute,
                    _args.display_debug,
                    _args.display_icons,
                    started_from,
                )

        # Configuration priority (debug as am example):
        # 1. Command-line argument: --debug
        # 2. Environment: CANOA_DEBUG
        # 3. Config: config.APP_DEBUG
        # 4. Code default
        # Considerations:
        #    In this project, there are several configs
        #    available, of which one is selected according to
        #    the 'app_mode' argument (: 'D', 'P', etc, see BaseConfig).
        #    If there is no app_mode, then
        #
        debug_4 = False
        debug_3 = debug_4  # Read above 'Considerations'
        debug_2 = bool(Fuse.get_os_env("debug", debug_3))
        fuse = Fuse(app_name, debug_2)
        fuse.display.info(
            f"The 'fuse' was started in {(app_mode_development if debug_2 else app_mode_production)} mode (and now we have how to print pretty)."
        )
        fuse.display.info(f"Current args: {fuse.args}.")
    except Exception as e:
        msg_error = _error_.format(__name__, "starting the fuse", e)

    return fuse, msg_error


# ---------------------------------------------------------------------------- #
from .BaseConfig import BaseConfig


def _ignite_config(app_mode) -> Tuple[BaseConfig, str]:
    """
    Select the config, based in the app_mode (production or debug)
    WARNING: Don't run with debug turned on in production!
    """
    config = None  # this config will later be 'globally shared' by shared
    msg_error = None
    _app_mode = ""
    try:
        from .config import app_mode_production, app_mode_development, get_config_for_mode

        if is_str_none_or_empty(app_mode):
            _app_mode = app_mode_development if fuse.app_debug else app_mode_production
        else:
            _app_mode = app_mode

        config = get_config_for_mode(_app_mode)
        if not config:
            raise (f"Unknown config mode {config}.")
        fuse.display.info(f"The app config, in '{_app_mode}' mode, was ignited.")
    except KeyError:
        msg_error = _error_.format(
            __name__,
            "selecting the <app_mode>",
            f"Expected values are [{app_mode_development}, {app_mode_production}].",
        )
    except Exception as e:
        msg_error = _error_.format(__name__, f"initializing the app config in  mode '{_app_mode}'", e)

    return config, msg_error


# ---------------------------------------------------------------------------- #
def _check_mandatory_keys(config) -> str:
    """Check if the mandatories environment variables are set."""

    msg_error = None
    try:
        from .BaseConfig import CONFIG_MANDATORY_KEYS

        def __is_empty(key: str) -> bool:
            value = getattr(config, key, "")
            empty = value is None or value.strip() == ""
            if empty:
                fuse.display.error(f"[{__name__}]: Config[{config.APP_MODE}].{key} has no value.")
            return empty

        has_empty = False
        for key in CONFIG_MANDATORY_KEYS:
            if __is_empty(key):
                has_empty = True

        msg_error = (
            None
            if not has_empty
            else _error_.format(
                __name__,
                "confirming the existence of the mandatory configuration keys",
                "",
            )
        )

    except Exception as e:
        msg_error = _error_.format(__name__, f"checking mandatory keys of config[`{config.APP_MODE}`].", e)

    return msg_error


# ---------------------------------------------------------------------------- #
def _ignite_server_address(config) -> Tuple[any, str]:
    """Confirm validity of the server address"""
    address = None  # this address will later be 'globally shared' by shared
    msg_error = None
    try:
        from collections import namedtuple
        from urllib.parse import urlparse

        Address = namedtuple("Address", "host, port")
        address = Address("", 0)

        default_scheme = "http://"
        url = urlparse(config.SERVER_ADDRESS, default_scheme, False)

        # There is a bug is Linux (?) url.hostname  & url.port are always None
        path = ["", ""] if is_str_none_or_empty(url.path) else f"{url.path}:".split(":")
        address = Address(
            path[0] if is_str_none_or_empty(url.hostname) else url.hostname,
            path[1] if is_str_none_or_empty(url.port) else url.port,
        )

        if is_str_none_or_empty(address.host) or (address.port == 0):
            msg_error = f"Invalid host or port address found in [{config.SERVER_ADDRESS}], parsed: {address.host}:{address.port}`."
        else:
            fuse.display.info(f"The Flask Server Address address will be '{address.host}:{address.port}'.")
            setattr(config, "SERVER_HOST", address.host)
            setattr(config, "SERVER_PORT", address.port)

    except Exception as e:
        fuse.display.error(
            f"`urlparse('{config.SERVER_ADDRESS}', '{default_scheme}') -> parsed: {address.host}:{address.port}`"
        )
        msg_error = _error_.format(
            __name__,
            f"parsing server address. Expect value is [HostName:Port], found: [{config.SERVER_ADDRESS}]",
            e,
        )

    return address, msg_error


# - ---------------------------------------------------------------------------- #
# - Public --------------------------------------------------------------------- #
# - ---------------------------------------------------------------------------- #
from .Shared import Shared
def ignite_shared(app_name, start_at) -> Tuple[Shared, bool]:
    global fuse

    fuse, error = _start_fuse(app_name, start_at)
    if error:
        _log_and_exit(error)
    fuse.display.debug("The fuse was created.")

    # Config
    config, error = _ignite_config(fuse.app_mode)
    if error:
        _log_and_exit(error)
    fuse.display.debug("Config was ignited.")


    # Mandatory Configuration keys
    error = _check_mandatory_keys(config)
    if error:
        _log_and_exit(error)
    fuse.display.debug("All mandatory configuration keys were informed.")

    # Server Address
    address, error = _ignite_server_address(config)
    if error:
        _log_and_exit(error)
    fuse.display.debug("Flask Server Address is ready and 'config' configured.")


    shared = Shared(fuse.app_debug, config, fuse.display, address)
    fuse.display.info("The global var 'shared' was ignited.")

    # ---------------------------------------------------------------------------- #
    # Give warnings of import configuration that may be missing
    from .helpers.py_helper import is_str_none_or_empty

    warns = 0
    if is_str_none_or_empty(config.EMAIL_API_KEY):
        warns += 1
        fuse.display.warning(f"Sendgrid API key was not found, the app will not be able to send emails.")

    if is_str_none_or_empty(config.EMAIL_ORIGINATOR):
        warns += 1
        fuse.display.warning(
            f"The app email originator is not defined, the app will not be able to send emails."
        )

    fuse.display.info(f"{__name__} completed with 0 errors and {warns} warnings.")

    return shared, fuse.args.display_mute_after_init


# - ---------------------------------------------------------------------------- #
def ignite_sql_alchemy(app, shared):

    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy import create_engine, select

    sa = SQLAlchemy(app)
    try:
        engine = create_engine(shared.config.SQLALCHEMY_DATABASE_URI)
        with engine.connect() as connection:
            connection.scalar(select(1))
            shared.display.debug("The database connection is active.")

    except Exception as e:
        _log_and_exit(f"Unable to connect to the database. Error details: [{e}].")

    # Obfuscate the password of SQLALCHEMY_DATABASE_URI value
    import re

    db_uri_safe = re.sub(
        shared.config.SQLALCHEMY_DATABASE_URI_REMOVE_PW_REGEX,
        shared.config.SQLALCHEMY_DATABASE_URI_REPLACE_PW_STR,
        shared.config.SQLALCHEMY_DATABASE_URI,
    )

    # it (seems) that SQLAlchemy obfuscate the strConn, so I do as well
    # as it should not be needed any more (just for info)
    shared.config.SQLALCHEMY_DATABASE_URI = db_uri_safe

    return sa


# eof
