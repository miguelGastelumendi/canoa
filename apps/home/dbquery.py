from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import text
from .. import config

def getEngine():
    return create_engine(config.Config.SQLALCHEMY_DATABASE_URI)


def getSession():
    session_factory = sessionmaker(getEngine())
    return scoped_session(session_factory)


def connectDB():
    engine = getEngine()
    return engine.connect()


def executeSQL(sql):
    conn = connectDB()
    try:
        return conn.execute(text(sql))
    except Exception as e:
        raise e


def getValueFromDb(sql):
    rows = executeSQL(sql)
    for row in rows:
        return row[0]
    return None

def getDictResultset(sql):
    return {row[0]: row[1] for row in executeSQL(sql)}


def getJSONResultset(sql):
    return executeSQL(sql).first()[0]


def getDataframeResultSet(sql):
    return pd.read_sql(sql, connectDB())

