# -*- encoding: utf-8 -*-
"""
 Equipe da Canoa -- 2024

 mgd 2024-05-06
"""
# cSpell:ignore  SQLALCHEMY,

from os import path, getenv as os_getenv
from .scripts.pyHelper import is_str_none_or_empty

class Config():

    def app_name() -> str:
        return 'Canoa'

    def getenv(key: str, default=None) -> str:
        _key = None if is_str_none_or_empty(key) else f"{Config.app_name().upper()}_{key}"
        return os_getenv(_key, default)

    email_originator = "assismauro@hotmail.com"

    basedir = path.abspath(path.dirname(__file__))

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = ''
    SQLALCHEMY_DATABASE_URI = ''
    SERVER_ADDRESS = ''
    EMAIL_API_KEY =  ''
    DEBUG = False


# Configuration Environment Variables
Config.SECRET_KEY = Config.getenv('SECRET_KEY', 'S#perS3crEt_007')
Config.EMAIL_API_KEY = Config.getenv('EMAIL_API_KEY')
Config.SQLALCHEMY_DATABASE_URI = Config.getenv('SQLALCHEMY_DATABASE_URI')
Config.ASSETS_ROOT = Config.getenv('ASSETS_ROOT', '/static/assets')
Config.SERVER_ADDRESS = Config.getenv('SERVER_ADDRESS', '0.0.0.0:5000')
Config.DEBUG = (Config.getenv('DEBUG', 'False') == 'True')   # from run.py 2024.05.10

if (Config.SQLALCHEMY_DATABASE_URI == '') or (Config.EMAIL_API_KEY == ''):
    exit("Verifique se as variáveis de ambiente estão definidas.")

# Load all possible configurations
config_dict = {
    'Production': Config,
    'Debug'     : Config
}

#eof