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

# Get environment variables
# https://flask.palletsprojects.com/en/latest/config/
# Couldn't make work (VC seems to change venv)
#   https://flask.palletsprojects.com/en/latest/api/#flask.Config.from_prefixed_env


# Base Class for App Config
# https://flask.palletsprojects.com/en/latest/config/
class BaseConfig():
    app_name = 'Canoa'
    #major.minor.patch,
    app_version =  'α 1.36' # 1.36' &beta β;
    environ_prefix = f"{app_name.upper()}_"


    def get_os_env(key: str, default = None) -> str:
        _key = None if is_str_none_or_empty(key) else BaseConfig.environ_prefix
        return os_getenv(_key, default)

    EMAIL_ORIGINATOR = 'assismauro@hotmail.com'
    ROOT_FOLDER = path.abspath(path.dirname(__file__))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = ''
    SQLALCHEMY_DATABASE_URI = ''
    SERVER_ADDRESS = '127.0.0.1:5000'
    SERVER_EXTERNAL_ADDRESS = requests.get('https://checkip.amazonaws.com').text.strip()
    EMAIL_API_KEY =  ''
    DEBUG = False
    TESTING = False


#initialize BaseConfig
def init_envvar_of_config(cfg):
    for key, value in environ.items():
        attribute_name = key[len(BaseConfig.environ_prefix):]
        if not key.startswith(BaseConfig.environ_prefix):
            pass
        elif hasattr(cfg, attribute_name):
            value = bool(value) if value.capitalize() in [str(True), str(False)] else value
            setattr(cfg, attribute_name, value)
        elif BaseConfig.DEBUG:
            print(f"Warning: {attribute_name} is not defined in the class attributes, cannot set envvar value.")


# Init BasicConfig
# used for securely signing the session cookie (mgd: change every version)
unique = f"{BaseConfig.app_name} v{BaseConfig.app_version}".encode()
BaseConfig.SECRET_KEY = sha384(unique).hexdigest()

init_envvar_of_config(BaseConfig)



# Debug Config
class DebugConfig(BaseConfig):
    SERVER_ADDRESS = 'http://127.0.0.1:5000'
    DEBUG = True

# Production Config
class ProductionConfig(BaseConfig):
    DEBUG = False  #Just to be sure & need some code here

# Load all possible configurations
config_modes = {
    'Production': ProductionConfig(),
    'Debug'     : DebugConfig()
}

#eof