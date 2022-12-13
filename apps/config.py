# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    # SECRET_KEY = config('SECRET_KEY'  , default='S#perS3crEt_007')
    SECRET_KEY = os.getenv('SECRET_KEY', 'S#perS3crEt_007')

    # This will create a file in <app> FOLDER
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    '''
    Refs: https://docs.sqlalchemy.org/en/14/dialects/mssql.html#dsn-connections
          https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16#ubuntu17

    Calc URI based on pyodbc string connection:

from sqlalchemy.engine import URL
connection_string='DRIVER={ODBC Driver 18 for SQL Server};SERVER=54.207.37.232,30310;DATABASE=RURALLEGAL;ENCRYPT=no;UID=rlatrium;PWD=Hibisco@12'
connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
# testing:
from sqlalchemy.engine import create_engine
engine = create_engine(connection_url)

    Original string:
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://mauro:Araticum@12@data.atriumforest.com.br:/APPSPEED?driver=ODBC+Driver+18+for+SQL+Server'
    '''
    # SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://?odbc_connect=DRIVER%3D%7BODBC+Driver+18+for+SQL+Server%7D%3BSERVER%3Dtcp%3A54.207.37.232%2C30310%3BDATABASE%3DRURALLEGAL%3BENCRYPT%3Dno%3BUID%rlatrium%3BPWD%3DHibisco@12%4012'
    # SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://?odbc_connect=DRIVER%3D%7BODBC+Driver+18+for+SQL+Server%7D%3BSERVER%3D54.207.37.232%2C30310%3BDATABASE%3DRURALLEGAL%3BENCRYPT%3Dno%3BUID%3Drlatrium%3BPWD%3DHibisco%4012'
    SQLALCHEMY_DATABASE_URI =   'mssql+pyodbc://?odbc_connect=DRIVER%3D%7BODBC+Driver+17+for+SQL+Server%7D%3BSERVER%3D54.207.37.232%2C30310%3BDATABASE%3DRURALLEGAL%3BENCRYPT%3Dno%3BUID%3Drlatrium%3BPWD%3DHibisco%4012'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')

class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
        os.getenv('DB_ENGINE'   , 'mysql'),
        os.getenv('DB_USERNAME' , 'appseed_db_usr'),
        os.getenv('DB_PASS'     , 'pass'),
        os.getenv('DB_HOST'     , 'localhost'),
        os.getenv('DB_PORT'     , 3306),
        os.getenv('DB_NAME'     , 'appseed_db')
    )

class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
