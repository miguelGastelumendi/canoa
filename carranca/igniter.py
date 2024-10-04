"""
 Equipe da Canoa -- 2024

 Classes Initializer

 mgd 2024-10-03

 """

# cSpell:ignore sqlalchemy mandatories cssless

from typing import Tuple

_error_ = "[{0}]: An error ocurred while {1}. Message `{2}`."


# ---------------------------------------------------------------------------- #
def do_fuse(app_name):  # -> Tuple[any, str]:
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
                )

        fuse = Fuse()
        fuse.display.info("The `fuse` was started successfully.")
    except Exception as e:
        msg_error = _error_.format(__name__, "starting the fuse", e)

    return fuse, msg_error


# ---------------------------------------------------------------------------- #
def ignite_config(fuse: any) -> Tuple[any, str]:
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
        fuse.display.info(f"The app config, in `{_app_mode}` mode, was initialized successfully.")
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
def check_mandatory_keys(fuse, app_config) -> Tuple[any, str]:
    """Check if the mandatories environment variables are set."""

    dummy = None  # this app_config will later be 'globally shared' by shared
    msg_error = None
    try:
        from .config import MANDATORY_KEYS

        def __is_empty(key: str) -> bool:
            value = getattr(app_config, key, "")
            empty = value is None or value.strip() == ""
            if empty:
                fuse.display.error(f"[{__name__}]: Config[{app_config.APP_MODE}].{key} has no value.")
            return empty

        has_empty = False
        for key in MANDATORY_KEYS:
            if __is_empty(key):
                has_empty = True

        msg_error = (
            ""
            if not has_empty
            else _error_.format(__name__, "confirming the existence of the mandatory configuration keys", "")
        )

    except Exception as e:
        msg_error = _error_.format(__name__, f"checking mandatory keys of `{app_config.__name__}`", e)

    return dummy, msg_error


# ---------------------------------------------------------------------------- #
def ignite_server_address(fuse, app_config) -> Tuple[any, str]:
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
def do_app(fuse, app_config) -> Tuple[any, str]:

    shared = None  # this is the 'globally shared' obj
    msg_error = None
    obj_name = "app"
    try:

        # https://flask.palletsprojects.com/en/latest/tutorial/factory/
        from flask import Flask

        app = Flask(fuse.app_name)
        app.config.from_object(app_config)

        obj_name = "shared"
        from .Shared import shared

        shared.initialize(app, app_config)
        shared.bind()

        # Obfuscate the string connection, we should not need it any more
        import re
        from .config import SQLALCHEMY_DB_URI

        db_uri_key = SQLALCHEMY_DB_URI
        db_uri_safe = re.sub(
            app_config.SQLALCHEMY_DATABASE_URI_REMOVE_PW_REGEX,
            app_config.SQLALCHEMY_DATABASE_URI_REPLACE_PW_STR,
            getattr(app_config, db_uri_key),
        )
        setattr(app_config, db_uri_key, db_uri_safe)

        if app_config.APP_MINIFIED:
            from flask_minify import Minify

            Minify(app=app, html=True, js=True, cssless=False)

    except Exception as e:
        msg_error = _error_.format(__name__, f"creating {obj_name}", e)

    return shared, msg_error


# eof
