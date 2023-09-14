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
connection_string='DRIVER={ODBC Driver 18 for SQL Server};SERVER=<IP>,<PORT>;DATABASE=<DATABASE>;ENCRYPT=no;UID=<USER>;PWD=<PASSWORD>'
connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
# testing:
from sqlalchemy.engine import create_engine
engine = create_engine(connection_url)

    Original string:
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://<USER>:<PASSWORD>@<SERVER>:/APPSPEED?driver=ODBC+Driver+18+for+SQL+Server'
    mgd: 'apagou os string connections'
'''
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    CHANGE_PWD_EMAIL_LINK = os.environ['CHANGE_PWD_EMAIL_LINK']

    if (SQLALCHEMY_DATABASE_URI == '') or (CHANGE_PWD_EMAIL_LINK == ''):
        raise Exception("Verifique se as variáveis de ambiente estão definidas.")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')

    MAPBOX_TOKEN = 'pk.eyJ1IjoiYXNzaXNtYXVybyIsImEiOiJja3RvcGt2eTgwZXc5Mm9taGd6MTltZ2o2In0.FJ2GqIssNuJxeYh0ewTpLw'

# Load all possible configurations
config_dict = {
    'Production': Config,
    'Debug'     : Config
}
