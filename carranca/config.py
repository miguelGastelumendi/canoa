"""
 Equipe da Canoa -- 2024

 Configuration Files for the Application

 mgd 2024-05-06
 mgd 2024-05-21: Base, Debug, Production
"""

# cSpell:ignore SQLALCHEMY

from typing import Dict
from hashlib import sha384
from os import path, getenv as os_getenv, environ

from carranca import app_name
from .igniter import fuse
from .helpers.wtf_helper import LenValidate
from .helpers.py_helper import is_str_none_or_empty

SQLALCHEMY_DB_URI = "SQLALCHEMY_DATABASE_URI"
MANDATORY_KEYS = [SQLALCHEMY_DB_URI, "SERVER_ADDRESS", "SECRET_KEY", "APP_MODE"]


# Base Class for App Config
# see https://flask.palletsprojects.com/en/latest/config/ for other attributes
class BaseConfig:
    """
    The Base Configuration Class for the App
    ----------------------------------------

    For the `data_validate` process's
    parameters/configuration see: ./config_upload.py
    """

    """ Environment Variables Helper
        ----------------------------
    """

    def get_os_env(key: str, default=None) -> str:
        _key = None if is_str_none_or_empty(key) else BaseConfig.envvars_prefix
        return os_getenv(_key, default)

    """ App Identification
        ----------------------------
    """
    APP_NAME = app_name

    # major.minor.patch
    APP_VERSION = "β 2.28"  # &beta;

    """ Internal attributes
        ------------------
    """
    # all environment variables begin with `Canoa_`
    envvars_prefix = f"{APP_NAME.upper()}_"

    # min & max text length for pw & user_name
    len_val_for_pw = LenValidate(6, 22)
    len_val_for_uname = LenValidate(3, 22)
    len_val_for_email = LenValidate(8, 60)

    """ Debugging And Info
        --------------------------
    """
    # see below (enum)
    APP_MODE = "None"
    APP_MINIFIED = None  # None = True if DEBUG else False
    # Flask https://flask.palletsprojects.com/en/latest/config/
    DEBUG = False
    TESTING = False
    SECRET_KEY = ""
    DEBUG_MSG = None  # None = True if DEBUG else False
    # Flask, trying to fix background shakes (CharGPT)
    SEND_FILE_MAX_AGE_DEFAULT = 31536000

    """ From Environment Variables
        --------------------------
    """
    # Root folder, see process.py
    ROOT_FOLDER = path.abspath(path.dirname(__file__))

    # see route_helper.py[is_external_ip_ready]
    EXTERNAL_IP_SERVICE = "https://checkip.amazonaws.com"

    # Email sender
    EMAIL_ORIGINATOR = "assismauro@hotmail.com"
    # Registered on the email API with key
    EMAIL_API_KEY = ""

    # Alchemy
    # SQLALCHEMY_DATABASE_URI = '' # added below
    SQLALCHEMY_DATABASE_URI_REMOVE_PW_REGEX = r":[^@]+@"
    SQLALCHEMY_DATABASE_URI_REPLACE_PW_STR = ":******@"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #
    SERVER_ADDRESS = ""
    # if left empty, an external service will be used
    # see self.EXTERNAL_IP_SERVICE
    # & ./helpers/route_helper.py[is_external_ip_ready()]
    SERVER_EXTERNAL_IP = ""
    SERVER_EXTERNAL_PORT = ""

    # initialize special attributes
    def init(self):
        def _if_debug(attrib):
            return bool(self.DEBUG if attrib is None else attrib)

        self.APP_MINIFIED = _if_debug(self.APP_MINIFIED)
        self.DEBUG_MSG = _if_debug(self.DEBUG_MSG)


# End Config
setattr(BaseConfig, SQLALCHEMY_DB_URI, "")
fuse.display.info("Preparing App Configs")


def init_envvar_of_config(cfg):
    """
    Initialize BaseConfig
    from environment variables
    """
    for key, value in environ.items():
        attribute_name = key[len(cfg.envvars_prefix) :]
        if not key.startswith(cfg.envvars_prefix):
            pass
        elif hasattr(cfg, attribute_name):
            value = bool(value) if value.capitalize() in [str(True), str(False)] else value
            if is_str_none_or_empty(value):
                fuse.display.warn(f"Ignoring empty envvar value for key [{key}], keeping original.")
            else:
                setattr(cfg, attribute_name, value)
        elif cfg.DEBUG:
            fuse.display.warn(
                f"[{attribute_name}] is not an attribute of `Config`, will not set envvar value."
            )


# === Retrieve values from envvars
init_envvar_of_config(BaseConfig)

if is_str_none_or_empty(BaseConfig.SECRET_KEY):
    """
    SECRET_KEY
    used for securely signing the session cookie (mgd: change every version)
    https://flask.palletsprojects.com/en/latest/config/#SECRET_KEY
    """
    unique = f"{BaseConfig.APP_NAME} v{BaseConfig.APP_VERSION}".encode()
    BaseConfig.SECRET_KEY = sha384(unique).hexdigest()


# === Available app/config modes, add yours here (extend )
app_mode_production: str = "Production"  # capital P
app_mode_debug: str = "Debug"  # capital D


# === Debug Config
class DebugConfig(BaseConfig):
    """
    The Debug Configuration Class for the App
    """

    # All IPs at port 5001
    SERVER_ADDRESS = (
        "http://0.0.0.0:5001"
        if is_str_none_or_empty(BaseConfig.SERVER_ADDRESS)
        else BaseConfig.SERVER_ADDRESS
    )
    DEBUG = True
    TESTING = True
    APP_MODE = app_mode_debug


# Production Config
class ProductionConfig(BaseConfig):
    """
    The Production Configuration Class for the App
    """

    DEBUG = False  # Just to be sure & need some code here
    TESTING = False
    APP_MODE = app_mode_production


# Load all possible configurations
config_modes: Dict[str, BaseConfig] = {
    app_mode_production: ProductionConfig(),
    app_mode_debug: DebugConfig(),
}

# eof
