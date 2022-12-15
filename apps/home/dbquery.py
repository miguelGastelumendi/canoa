from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import text
from apps import config
import json

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

def getLastId(tabeName: str)->int:
    return getValueFromDb(f"SELECT IDENT_CURRENT('{tabeName}')")

def getDictResultset(sql):
    return {row[0]: row[1] for row in executeSQL(sql)}

def getListDictResultset(sql):
    df = getDataframeResultset(sql)
    ret = []
    for _, row in df.iterrows():
        for i in range(len(row)):
            ret.append({df.columns[i]: row[i]})
    return ret


def getJSONResultset(sql):
    return executeSQL(sql).first()[0]


def getDataframeResultset(sql):
    return pd.read_sql(sql, connectDB())


def getListResultset(sql):
    return [row[0] for row in executeSQL(sql)]

