"""
 Equipe da Canoa -- 2024

 Configuration Files for the Application
----------------------------------------
 /!\ Attention
 ---------------------------------------
    This file position is VERY important
    `app_folder` must point to the folder
    where main.py is located



 mgd 2024-05-06
 mgd 2024-05-21: Base, Debug, Production
 mgd 2024-10-11: new file for BaseConfig, simplify imports


"""

# cSpell:ignore SQLALCHEMY searchpath

from os import path
from flask import Config
import logging

from ..common.app_constants import APP_NAME, APP_VERSION
from ..helpers.file_helper import path_remove_last_folder

CONFIG_MANDATORY_KEYS = [
    "SQLALCHEMY_DATABASE_URI",
    "SERVER_ADDRESS",
    "SECRET_KEY",
    "APP_MODE",
]

# === Available app/config modes, add yours own mode here (extend)
app_mode_production: str = "Production"  # capital P
app_mode_development: str = "Development"  # capital D
# ---------------------------
# Get the folder from main.py
app_folder = path.abspath(path_remove_last_folder(path.dirname(__file__)))


# Base Class for App Config
# see https://flask.palletsprojects.com/en/latest/config/ for other attributes
class BaseConfig(Config):
    """
    The Base Configuration Class for the App
    ----------------------------------------

    For the `data_validate` process's
    parameters/configuration see: ./config_upload.py
    """

    """ App Identification
        ----------------------------
    """

    APP_NAME = APP_NAME
    APP_VERSION = APP_VERSION

    """ Canoa Configurations
        --------------------------
    """
    # This is the final debug state of the app.
    #  See _get_debug_2 & Fuse
    APP_DEBUGGING: bool = None
    # see initialize:
    #  several keys are set to APP_PROPAGATE_DEBUG
    #  when it's config value is None
    APP_PROPAGATE_DEBUG = False
    # set in derived classes
    APP_DEBUG: bool = None
    APP_MINIFIED: bool = None  # <- True if APP_PROPAGATE_DEBUG else False
    APP_DISPLAY_DEBUG_MSG: bool = None  # <- True if APP_PROPAGATE_DEBUG else False
    APP_MODE = "None"  # see below (enum)

    """ Helpers Configuration
        --------------------------
    """
    # Registered user on the email API
    EMAIL_ORIGINATOR = ""  # from os_environment
    EMAIL_ORIGINATOR_NAME = f"e-mail de {APP_NAME}"
    # "  with key
    EMAIL_API_KEY = ""  # from os_environment
    # Folders
    APP_FOLDER = app_folder
    # storage area (user_files, schema_icons...)
    COMMON_PATH = path_remove_last_folder(app_folder)

    # My address service is SERVER_EXTERNAL_IP is empty
    # (used to send recovery email confirmation, etc)
    EXTERNAL_IP_SERVICE = "https://checkip.amazonaws.com"
    # satelier.dev.br
    SERVER_EXTERNAL_IP = "177.43.119.39"
    SERVER_EXTERNAL_PORT = ""

    """ Flask Configuration
        --------------------------
        https://flask.palletsprojects.com/en/latest/config/
        this must be set individually for each APP_MODE (see config.py)
        to send envvars directly to flask use the FLASK_ prefix
    """
    DEBUG: bool = None  # <- True if APP_PROPAGATE_DEBUG else False
    TESTING: bool = None  # <- True if APP_PROPAGATE_DEBUG else False
    DEBUG_TEMPLATES: bool = None  # <- True if APP_PROPAGATE_DEBUG else False
    # this does'nt work (spend a day to find out), is SERVER_NAME: SERVER_ADDRESS = ""
    # https://flask.palletsprojects.com/en/latest/config/#SERVER_NAME
    # Inform the application what host and port it is bound to (NO Scheme).
    # SERVER_NAME = "" use it after understand how
    PREFERRED_URL_SCHEME = ""
    SECRET_KEY = ""
    SESSION_COOKIE_NAME = f"{APP_NAME.lower()}"

    """ SQLAlchemy
        --------------------------
    """
    SQLALCHEMY_DATABASE_URI = ""  # from os_environment
    SQLALCHEMY_DATABASE_URI_REMOVE_PW_REGEX = r":[^@]+@"
    SQLALCHEMY_DATABASE_URI_REPLACE_PW_STR = ":*******@"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    """ Log to file configuration
        --------------------------
    """
    LOG_TO_FILE = True  # Log
    LOG_MIN_LEVEL = logging.INFO
    # folder is log_files
    LOG_FILE_FOLDER: str = None  # "log_files"
    LOG_FILE_NAME: str = None  # defaults to APP_NAME.datetime.log
    LOG_FILE_STATUS = "?"  # internal set


# eof
