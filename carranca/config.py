# -*- encoding: utf-8 -*-
"""
 Equipe da Canoa -- 2024

 mgd 2024-05-06
 mgd 2024-05-21: Base, Debug, Production
"""
# cSpell:ignore  SQLALCHEMY,

import requests
from hashlib import sha384
from os import path, getenv as os_getenv, environ
from .helpers.py_helper import is_str_none_or_empty


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

    For the `data_validate` process's
      parameters/configuration see: ./private/upload_file/Params.py
    """
    app_name = 'Canoa'
    #major.minor.patch,
    app_version =  'α 0.50' # &beta β;
    envvars_prefix = f"{app_name.upper()}_"
    app_mode = 'None'


    def get_os_env(key: str, default = None) -> str:
        _key = None if is_str_none_or_empty(key) else BaseConfig.envvars_prefix
        return os_getenv(_key, default)

    EMAIL_ORIGINATOR = 'assismauro@hotmail.com'
    EMAIL_API_KEY =  ''

    ROOT_FOLDER = path.abspath(path.dirname(__file__))

    SECRET_KEY = ''
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SERVER_ADDRESS = ''
    SERVER_EXTERNAL_ADDRESS = requests.get('https://checkip.amazonaws.com').text.strip()

    ASSETS_ROOT = '/static/assets'
    DEBUG = False
    TESTING = False


# === Init BasicConfig
def init_envvar_of_config(cfg):
    for key, value in environ.items():
        attribute_name = key[len(BaseConfig.envvars_prefix):]
        if not key.startswith(BaseConfig.envvars_prefix):
            pass
        elif hasattr(cfg, attribute_name):
            value = bool(value) if value.capitalize() in [str(True), str(False)] else value
            setattr(cfg, attribute_name, value)
        elif BaseConfig.DEBUG:
            print(f"Warning: {attribute_name} is not defined in the class attributes, cannot set envvar value.")

# Retrieve values from envvars
init_envvar_of_config(BaseConfig)

# SECRET_KEY
# used for securely signing the session cookie (mgd: change every version)
# https://flask.palletsprojects.com/en/latest/config/#SECRET_KEY
if is_str_none_or_empty(BaseConfig.SECRET_KEY):
    unique = f"{BaseConfig.app_name} v{BaseConfig.app_version}".encode()
    BaseConfig.SECRET_KEY = sha384(unique).hexdigest()

# === Available app/config modes, add yours here (extend )
app_mode_production = 'Production' # capital P
app_mode_debug = 'Debug' # capital D


# Debug Config
class DebugConfig(BaseConfig):
    """
    The Debug Configuration Class for the App
    """

    SERVER_ADDRESS = 'http://127.0.0.1:5000' if is_str_none_or_empty(BaseConfig.SERVER_ADDRESS) else BaseConfig.SERVER_ADDRESS
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
""" List[BaseConfiguration]  list of configuration modes """
config_modes = {
    app_mode_production: ProductionConfig(),
    app_mode_debug     : DebugConfig()
}

#eof