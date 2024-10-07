"""
#igniter.py
   Common classes initializer and
   basic configuration validator module

   Equipe da Canoa -- 2024
   mgd 2024-10-01
"""

# cSpell:ignore sqlalchemy mandatories cssless sendgrid, ENDC

from typing import Tuple

_error_ = "[{0}]: An error ocurred while {1}. Message `{2}`."
fuse = None


# ---------------------------------------------------------------------------- #
def _start_fuse(app_name: str, started_from: float) -> Tuple[any, str]:
    """
    Create the 'fuse' that will ignite all the initializations classes
    """
    msg_error = None
    fuse = None
    try:
        from .Args import Args
        from .helpers.Display import Display
        from .helpers.py_helper import set_flags_from_argv

        class Fuse:
            def __init__(self):
                self.app_name = app_name
                _args = Args(True)
                self.args = set_flags_from_argv(_args)
                self.display = Display(
                    f"{self.app_name}: ",
                    self.args.display_mute,
                    self.args.display_debug,
                    self.args.display_icons,
                    started_from,
                )

        fuse = Fuse()
        fuse.display.info("The 'fuse' was started. Now we have how to print nicely.")
        fuse.display.info(f"Current args: [{fuse.args}].")
    except Exception as e:
        msg_error = _error_.format(__name__, "starting the fuse", e)

    return fuse, msg_error


# ---------------------------------------------------------------------------- #
def _ignite_config() -> Tuple[any, str]:
    """
    Select the app_config, based in the app_mode (production or debug)
    WARNING: Don't run with debug turned on in production!
    """
    app_config = None  # this app_config will later be 'globally shared' by shared
    msg_error = None
    try:
        from .config import (
            app_mode_production,
            app_mode_debug,
            config_modes,
            BaseConfig,
        )

        # 1. argument --debug
        _app_mode = app_mode_debug if fuse.args.debug else app_mode_production
        # 2. environment
        _app_mode = BaseConfig.get_os_env("APP_MODE", app_mode_debug)
        # 3. load & init
        app_config = config_modes[_app_mode]
        app_config.init()
        fuse.display.info(f"The app config, in `{_app_mode}` mode, was ignited.")
    except KeyError:
        msg_error = _error_.format(
            __name__,
            "selecting the <app_mode>",
            f"Expected values are [{app_mode_debug}, {app_mode_production}].",
        )
    except Exception as e:
        msg_error = _error_.format(__name__, "initializing the app config", e)

    return app_config, msg_error


# ---------------------------------------------------------------------------- #
def _check_mandatory_keys(app_config) -> str:
    """Check if the mandatories environment variables are set."""

    msg_error = None
    try:
        from .config import CONFIG_MANDATORY_KEYS

        def __is_empty(key: str) -> bool:
            value = getattr(app_config, key, "")
            empty = value is None or value.strip() == ""
            if empty:
                fuse.display.error(
                    f"[{__name__}]: Config[{app_config.APP_MODE}].{key} has no value."
                )
            return empty

        has_empty = False
        for key in CONFIG_MANDATORY_KEYS:
            if __is_empty(key):
                has_empty = True

        msg_error = (
            ""
            if not has_empty
            else _error_.format(
                __name__,
                "confirming the existence of the mandatory configuration keys",
                "",
            )
        )

    except Exception as e:
        msg_error = _error_.format(
            __name__, f"checking mandatory keys of `{app_config.__name__}`", e
        )

    return msg_error


# ---------------------------------------------------------------------------- #
def _ignite_server_address(app_config) -> Tuple[any, str]:
    """Confirm validity of the server address"""
    address = None  # this app_config will later be 'globally shared' by shared
    msg_error = None
    try:
        from collections import namedtuple
        from urllib.parse import urlparse

        from .helpers.py_helper import is_str_none_or_empty

        Address = namedtuple("Address", "host, port")
        address = Address("", 0)

        default_scheme = "http://"
        url = urlparse(app_config.SERVER_ADDRESS, default_scheme, False)

        # There is a bug is Linux (?) url.hostname  & url.port are always None
        path = ["", ""] if is_str_none_or_empty(url.path) else f"{url.path}:".split(":")
        address = Address(
            path[0] if is_str_none_or_empty(url.hostname) else url.hostname,
            path[1] if is_str_none_or_empty(url.port) else url.port,
        )

        if is_str_none_or_empty(address.host) or (address.port == 0):
            msg_error = f"Invalid host or port address found in [{app_config.SERVER_ADDRESS}], parsed: {address.host}:{address.port}`."
        else:
           fuse.display.info(f"The address will be '{address.host}:{address.port}'.")


    except Exception as e:
        fuse.display.error(
            f"`urlparse('{app_config.SERVER_ADDRESS}', '{default_scheme}') -> parsed: {address.host}:{address.port}`"
        )
        msg_error = _error_.format(
            __name__,
            f"parsing server address. Expect value is [HostName:Port], found: [{app_config.SERVER_ADDRESS}]",
            e,
        )

    return address, msg_error


# ---------------------------------------------------------------------------- #
def _ignite_shared(app_config) -> str:

    msg_error = None
    shared = None
    obj_name = "obfuscation"
    try:
        import re
        # Obfuscate the password of SQLALCHEMY_DATABASE_URI value
        db_uri_safe = re.sub(
            app_config.SQLALCHEMY_DATABASE_URI_REMOVE_PW_REGEX,
            app_config.SQLALCHEMY_DATABASE_URI_REPLACE_PW_STR,
            app_config.SQLALCHEMY_DATABASE_URI,
        )

        obj_name = "shared"
        from .Shared import Shared

        shared = Shared()
        shared.initialize(app_config, fuse.display)

        # shared.initialize() turns None app_config.SQLALCHEMY_DATABASE_URI
        # lets just obfuscate the pw
        app_config.SQLALCHEMY_DATABASE_URI= db_uri_safe

        fuse.display.info("The global var 'shared' was ignited.")
    except Exception as e:
        msg_error = _error_.format(__name__, f"instantiating {obj_name}", e)

    return shared, msg_error


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# Escape Door
def _log_and_exit(ups: str):
    if fuse:
        fuse.display.error(ups)
    exit(ups)


# - ---------------------------------------------------------------------------- #
# - Ignite --------------------------------------------------------------------- #
# - ---------------------------------------------------------------------------- #
def create_shared(app_name, start_at):
    global fuse

    fuse, error = _start_fuse(app_name, start_at)
    if error:
        _log_and_exit(error)
    fuse.display.debug("The fuse was created.")

    # Config
    app_config, error = _ignite_config()
    if error:
        _log_and_exit(error)
    fuse.display.debug("Config was ignited.")

    # Mandatory Configuration keys
    error = _check_mandatory_keys(app_config)
    if error:
        _log_and_exit(error)
    fuse.display.debug("All mandatory configuration keys were informed.")

    # Server Address
    address, error = _ignite_server_address(app_config)
    if error:
        _log_and_exit(error)
    # alternative configuration to Flask
    setattr(app_config, "SERVER_HOST",  address.host)
    setattr(app_config, "SERVER_PORT", address.port)
    fuse.display.debug("Server Address is ready and 'app_config' configured.")

    # app
    shared, error = _ignite_shared(app_config)
    if error:
        _log_and_exit(error)

    shared.address = address

    # ---------------------------------------------------------------------------- #
    # Give warnings of import configuration that may be missing
    from .helpers.py_helper import is_str_none_or_empty
    warns = 0
    if is_str_none_or_empty(app_config.EMAIL_API_KEY):
        warns += 1
        fuse.display.warning(
            f"Sendgrid API key was not found, the app will not be able to send emails."
        )

    if is_str_none_or_empty(app_config.EMAIL_ORIGINATOR):
        warns += 1
        fuse.display.warning(
            f"The app email originator is not defined, the app will not be able to send emails."
        )

    fuse.display.info(
        f"{__name__} completed with 0 errors and {warns} warnings."
    )

    return shared

# eof
