# -*- encoding: utf-8 -*-
"""
 Equipe da Canoa -- 2024

 mgd 2024-05-06
 mgd 2024-05-21: Base, Debug, Production
"""
# cSpell:ignore SQLALCHEMY

from hashlib import sha384
from typing import Dict
from os import path, getenv as os_getenv, environ
from .helpers.py_helper import is_str_none_or_empty
from .helpers.wtf_helper import LenValidate


# from collections import UserDict
# class MyCustomDict(UserDict):
#     def __getattr__(self, attr):
#         if attr in self.data:
#             return self.data[attr]
#         else:
#             raise AttributeError(f"'MyCustomDict' object has no attribute '{attr}'")



# Base Class for App Config
# see https://flask.palletsprojects.com/en/latest/config/ for other attributes
class BaseConfig:
    """
        The Base Configuration Class for the App
        ----------------------------------------

        For the `data_validate` process's
        parameters/configuration see: ./config_upload.py
    """

    ''' Environment Variables Helper
        ----------------------------
    '''
    def get_os_env(key: str, default = None) -> str:
        _key = None if is_str_none_or_empty(key) else BaseConfig.envvars_prefix
        return os_getenv(_key, default)

    ''' Internal attributes
        ------------------
    '''
    app_name = 'Canoa'
    #major.minor.patch,
    app_version =  'β 2.1' # &beta
    # see below (enum)
    app_mode = 'None'
    # all environment variables begin with `Canoa_`
    envvars_prefix = f"{app_name.upper()}_"

    # min & max text length for pw & user_name
    len_val_for_pw = LenValidate(6, 22)
    len_val_for_uname = LenValidate(3, 22)


    ''' From Environment Variables
        --------------------------
    '''

    # Root folder, see process.py
    ROOT_FOLDER = path.abspath(path.dirname(__file__))

    # see route_helper.py[is_external_ip_ready]
    EXTERNAL_IP_SERVICE = 'https://checkip.amazonaws.com'

    # Email sender
    EMAIL_ORIGINATOR = 'assismauro@hotmail.com'
    # Registered on the email API with key
    EMAIL_API_KEY =  ''

    SECRET_KEY = ''
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    SERVER_ADDRESS = ''
    # if left empty, an external service will be used
    # see self.EXTERNAL_IP_SERVICE
    # & ./helpers/route_helper.py[is_external_ip_ready()]
    SERVER_EXTERNAL_IP = ''
    SERVER_EXTERNAL_PORT = ''

    ASSETS_ROOT = '/static/assets'
    DEBUG = False
    TESTING = False


def init_envvar_of_config(cfg):
    """
    Initialize BaseConfig
    from environment variables
    """
    for key, value in environ.items():
        attribute_name = key[len(BaseConfig.envvars_prefix):]
        if not key.startswith(BaseConfig.envvars_prefix):
            pass
        elif hasattr(cfg, attribute_name):
            value = bool(value) if value.capitalize() in [str(True), str(False)] else value
            if is_str_none_or_empty(value):
                print(f"Ignoring empty envvar value for key [{key}], keeping original." )
            else:
                setattr(cfg, attribute_name, value)
        elif BaseConfig.DEBUG:
            print(f"[{attribute_name}] is not an attribute of `Config`, will not set envvar value.")

# === Retrieve values from envvars
init_envvar_of_config(BaseConfig)

if is_str_none_or_empty(BaseConfig.SECRET_KEY):
    """
    SECRET_KEY
    used for securely signing the session cookie (mgd: change every version)
    https://flask.palletsprojects.com/en/latest/config/#SECRET_KEY
    """
    unique = f"{BaseConfig.app_name} v{BaseConfig.app_version}".encode()
    BaseConfig.SECRET_KEY = sha384(unique).hexdigest()


# === Available app/config modes, add yours here (extend )
app_mode_production : str = 'Production' # capital P
app_mode_debug : str = 'Debug' # capital D


# === Debug Config
class DebugConfig(BaseConfig):
    """
    The Debug Configuration Class for the App
    """

    # All IPs at port 5001
    SERVER_ADDRESS = 'http://0.0.0.0:5001' if is_str_none_or_empty(BaseConfig.SERVER_ADDRESS) else BaseConfig.SERVER_ADDRESS
    DEBUG = True
    app_mode = app_mode_debug

# Production Config
class ProductionConfig(BaseConfig):
    """
    The Production Configuration Class for the App
    """
    DEBUG = False  #Just to be sure & need some code here
    app_mode = app_mode_production


# Load all possible configurations
config_modes: Dict[str, BaseConfig] = {
    app_mode_production: ProductionConfig(),
    app_mode_debug     : DebugConfig()
}

# eof