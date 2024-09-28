
# cSpell:ignore sqlalchemy keepalives

from db_helper import executeSQL


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