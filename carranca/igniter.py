"""
#igniter.py
   Common classes initializer and
   basic configuration validator module

   Equipe da Canoa -- 2024
   mgd 2024-10-01--07
"""

# cSpell:ignore sqlalchemy app_name cssless sendgrid ENDC psycopg2 mandatories

from typing import Tuple, Any
from .helpers.py_helper import is_str_none_or_empty

from .Args import Args

_error_ = "[{0}]: An error ocurred while {1}. Message `{2}`."
fuse = None


# ---------------------------------------------------------------------------- #
# Escape Door
def _log_and_exit(ups: str):
    if fuse and fuse.display:
        fuse.display.error(ups)
    exit(ups)


# ---------------------------------------------------------------------------- #
# Fuse a igniter helper
class Fuse:
    def __init__(self, app_name, display: Any, args: Args):
        from .BaseConfig import app_mode_production, app_mode_development

        self.app_name = app_name
        self.app_debug = args.app_debug
        self.display = display
        self.args = args

        if is_str_none_or_empty(args.app_mode):
            self.app_mode = app_mode_development if args.app_debug else app_mode_production
        else:
            self.app_mode = self.args.app_mode


# ---------------------------------------------------------------------------- #
def _get_debug_2(app_name: str) -> bool:

    # Configuration priority (debug as am example):
    # 1. Command-line argument (sys.argv): --debug
    # 2. Environment: CANOA_DEBUG
    # 3. Config: config.APP_DEBUG
    # 4. Code default values
    # Considerations:
    #    In this project, there are several configs
    #    available, of which one is selected according to
    #    the 'app_mode' argument (: 'D', 'P', etc, see config.py).
    #    Taking this inb consideration, we skip 3. Config
    #
    from .helpers.user_helper import get_os_env

    debug_4 = False
    debug_3 = debug_4  # Read above 'Considerations'
    debug_2 = bool(get_os_env("debug", debug_3, app_name))
    return debug_2


# ---------------------------------------------------------------------------- #
def _start_fuse(app_name: str, args: Args, started_from: float) -> Tuple[any, str]:
    """
    Create the 'fuse' that will assists the initializations of classes
    """
    msg_error = None
    fuse = None
    try:
        from .helpers.Display import Display

        display = Display(
            f"{app_name}: ",
            args.display_mute,
            args.display_debug,
            args.display_icons,
            started_from,
        )
        fuse = Fuse(app_name, display, args)
        fuse.display.info(
            f"The 'fuse' was started in {fuse.app_mode} mode (and now we have how to print pretty)."
        )
        fuse.display.info(f"Current args: {fuse.args}.")
    except Exception as e:
        msg_error = _error_.format(__name__, "starting the fuse", e)

    return fuse, msg_error


# ---------------------------------------------------------------------------- #
from .DynamicConfig import DynamicConfig


def _ignite_config(app_mode) -> Tuple[DynamicConfig, str]:
    """
    Select the config, based in the app_mode (production or debug)
    WARNING: Don't run with debug turned on in production!
    """
    config = None  # this config will later be 'shared' by shared
    msg_error = None
    try:
        from .DynamicConfig import get_config_for_mode

        config = get_config_for_mode(app_mode)
        if config is None:
            raise Exception(f"Unknown config mode {config}.")
        fuse.display.info(f"The app config, in '{app_mode}' mode, was ignited.")
    except Exception as e:
        msg_error = _error_.format(__name__, f"initializing the app config in mode '{app_mode}'", e)

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
from .Shared import Shared, create_shared


def ignite_shared(app_name, start_at) -> Tuple[Shared, bool]:
    global fuse

    debug_2 = _get_debug_2(app_name)
    args = Args(debug_2).from_arguments()

    fuse, error = _start_fuse(app_name, args, start_at)
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
    _, error = _ignite_server_address(config)
    if error:
        _log_and_exit(error)
    fuse.display.debug("Flask Server Address is ready and 'config' configured.")

    # Create the global hub class 'shared'
    shared = create_shared(fuse.app_debug, config, fuse.display)
    fuse.display.info("The session 'shared'  variable was ignited.")

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
    display_mute_after_init = fuse.args.display_mute_after_init

    fuse = None  # not need it anymore

    return shared, display_mute_after_init


# - ---------------------------------------------------------------------------- #
def ignite_sql_connection(shared, uri):

    from sqlalchemy import create_engine, select
    try:
        engine = create_engine(uri)
        with engine.connect() as connection:
            connection.scalar(select(1))
            shared.display.info("The database connection is active.")

    except Exception as e:
        _log_and_exit(f"Unable to connect to the database. Error details: [{e}].")

    return


# - ---------------------------------------------------------------------------- #
def reignite_shared(app_name):
    global fuse

    import time
    from flask_sqlalchemy import SQLAlchemy

    ###   from main import app_name

    start_at = time.perf_counter()
    fuse, error = _start_fuse(app_name, start_at)

    # if error:
    #     fuse.display.error(f"The `fuse` was not create created: [{error}].")

    # # Config
    # config, error = _ignite_config(fuse.app_mode)
    # if error:
    #     fuse.display.error(f"The `config` was not create create: [{error}].")

    # Create the global hub class 'shared'
    shared = Shared(fuse.app_debug, fuse.display)
    fuse.display.info("The session 'shared' variable was reignited.")
    fuse = None  # not need it anymore
    # elif not shared.config.APP_DISPLAY_DEBUG_MSG:
    # shared.display.debug_output = False


# eof
