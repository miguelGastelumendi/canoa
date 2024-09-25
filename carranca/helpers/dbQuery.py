
# cSpell:ignore sqlalchemy keepalives

from sqlalchemy import create_engine, text
from ..shared import app_config

engine = create_engine(
    app_config.SQLALCHEMY_DATABASE_URI,
    isolation_level= 'AUTOCOMMIT', # "READ UNCOMMITTED", # mgd em Canoa, acho desnecessário
    pool_pre_ping= True,
    connect_args={
        # (https://www.postgresql.org/docs/current/libpq-connect.html)
        # Maximum time to wait while connecting, in seconds  was 600.
        # instead mhd is using `pool_pre_ping` and set connect_timeout to 10
        'connect_timeout': 10
        ,'application_name': app_config.APP_NAME
        ,'keepalives': 1
    }
)


def executeSQL(sql):
    global engine
    with engine.connect() as conn:
        return conn.execute(text(sql))

def getValues(sql):
    rows = executeSQL(sql)
    try:
        lines = rows.fetchall()
        l = []
        if len(lines) > 1:
            for line in lines:
                l.append(line[0])
            return tuple(l)
        elif len(lines[0]) > 1:
            for v in lines[0]:
                l.append(v)
            return tuple(l)
        else:
            return lines[0][0]
    except:
        return None

def getLastId(tabeName: str)->int:
    return getValues(f"SELECT IDENT_CURRENT('{tabeName}')")

def getDictResultSet(sql):
    return {row[0]: row[1] for row in executeSQL(sql)}

#eof