# Package/__init__.py
# This file, is execute by the Python interpreter on startup once

"""
    The main script ;-)

    For newbies, remember:
       Canoa/
        ├── LocalDrive         # git ignored folder for project dev info
        ├── user_files         # git ignored folder with all the users files downloaded for validation
        ├── carranca/          # main application package
        |    ├── __init__.py   # crucial (tells Python that tis folder is a package (carranca). Creates the app
        │    ├── main.py       # <- You are here
        │    ├── shared.py     # shared var with most used object (app, app_config, db, etc)
        │    ├── config.py     # configuration file
        │    ├── config_..     # config_validate_process.py specific configurations for the validate process
        │    ├── helpers
        |    |    ├──:        # py files
        │    ├── private
        |    |    ├──:         # models, routes, forms py files
        |    |    ├── access_control
        |    |    |   └── password_change
        |    |    └── validate_process
        |    |         └──:     # py files required for the validation process
        │    ├── public
        |    |    ├──:          # models, routes, forms, etc py files
        |    |    └── access_control
        |    |         └──:     # password_reset, login, reset, password_recovery
        │    ├── static         # assets, css, docs, img, js
        │    └── templates      # jinja templates
        |         ├── accounts
        |         ├── home
        |         ├── includes
        |         ├── layouts
        |         └── private
        |
        ├── requirements.txt
        ├── README.md
        ├── .gitignore
        ├── mgd-logbook.txt my log file
        ├─: several bat/sh for to start data_validate
        ├─: IIS (MS Internet Information Services) configuration files *web.config
        └─: .env .git .vscode


    see https://flask.palletsprojects.com/en/latest/tutorial/factory/


    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore mandatories sqlalchemy, cssless sendgrid, ENDC

# ---------------------------------------------------------------------------- #
# Performance
import time

started = time.perf_counter()
fuse = None


# ---------------------------------------------------------------------------- #
# Helpers
def _error(msg):
    if fuse:
        fuse.display.error(msg)


def __log_and_exit(ups: str):
    _error(ups)
    exit(ups)


# - Ignite --------------------------------------------------------------------- #
# Fuse
from .igniter import do_fuse

fuse, error = do_fuse("Canoa")
if error: __log_and_exit(error)
fuse.display.debug(f"Starting {fuse.app_name}")

# Config
from .igniter import ignite_config

app_config, error = ignite_config(fuse)
if error: __log_and_exit(error)
fuse.display.debug("Config is ready")

# Mandatory Configuration keys
from .igniter import check_mandatory_keys

dummy, error = check_mandatory_keys(fuse, app_config)
if error: __log_and_exit(error)
fuse.display.debug("Mandatory configuration keys were informed.")

# Server Address
from .igniter import ignite_server_address

address, error = ignite_server_address(fuse, app_config)
if error: __log_and_exit(error)
fuse.display.debug("Server Address is ready")

# app
from .igniter import do_app

shared, error = do_app(fuse, app_config)
if error: __log_and_exit(error)
fuse.display.debug(
    f"{app_config.APP_NAME} Version {app_config.APP_VERSION} started in {app_config.APP_MODE} in mode :-)"
)
# if shared. :  # or to_str(args[1]):
#     from .public.debug_info import get_debug_info

#     get_debug_info(True)

# # ---------------------------------------------------------------------------- #
# # Give warnings of import configuration that may be missing
# if is_str_none_or_empty(app_config.EMAIL_API_KEY):
#     app.logger.warning(f"Sendgrid API key was not found, the app will not be able to send emails.")

# if is_str_none_or_empty(app_config.EMAIL_ORIGINATOR):
#     app.logger.warning(f"The app email originator is not defined, the app will not be able to send emails.")

# if is_str_none_or_empty(address.host) or (address.port == 0):
#     __log_and_exit(
#         f"Invalid hot or port address, found [{app_config.SERVER_ADDRESS}], parsed: {address.host}:{address.port}`"
#     )

# # ---------------------------------------------------------------------------- #
# # Ready to go, lunch!
# # msg= f"Expected '__main__' as __name__, but got '{__name__}' instead."
# # if __name__ == "__main__":
# elapsed = (time.perf_counter() - started) * 1000
# fuse.display.info(f"{__name__} ready in {elapsed:,.0f}ms", "")  # BUG prompt do instance
# fuse.display.info(f"Launching {app_config.APP_NAME} v {app_config.APP_VERSION}", "")
# # app.run(host=address.host, port=address.port, debug=False)
# # elif app_config.DEBUG:
# #     start.display.error(f"{msg} Cannot {app_config.APP_NAME}.")
# # else:
# #     __log_and_exit(f"{msg} Exiting...")

# # eof
