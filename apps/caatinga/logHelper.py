# -*- encoding: utf-8 -*-
from datetime import datetime
import apps.home.dbquery as dbquery
class Log():
    def __init__(self, fname: str):
        self.fname = fname
        self.buffer = ''

    def log(self, text: str):
        msg = f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S.%f")} {text}\n'
        if self.fname != '':
            with open(self.fname,mode='a') as logFile:
                logFile.write(msg)
        print(msg)

class Log2Database():
    def logActivity2Database(self, idUsuario: str, idProjeto: str, url: str):
        try:
            dbquery.executeSQL(f"""INSERT INTO RURALLEGAL.dbo.LogAcesso
    (idUsuario, Url, idProjeto)
    VALUES('{idUsuario}', '{url.replace(chr(39),chr(35))}', '{idProjeto}');
        """)
        except:
            pass


