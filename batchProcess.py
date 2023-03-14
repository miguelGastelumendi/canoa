# -*- encoding: utf-8 -*-
import apps.home.dbquery as dbquery
from apps.home.updateProjectDataSQL import sqls
from apps.config import Config

config = Config()

def calculateFinancials(idProjeto: int):
    print(f"idProjeto: {idProjeto}")
    for key in sqls.keys():
        result = dbquery.executeSQL(sqls[key].replace('@idProjeto',str(idProjeto)))
        print(f"{key} ({result.rowcount})")

def process():
    toProcess = dbquery.getDataframeResultset("select * from listaAProcessar")
    if len(toProcess) > 0:
        for _, row in toProcess.iterrows():
            calculateFinancials(row.idProjeto)
            dbquery.executeSQL(f"delete from listaAProcessar where idProjeto = {row.idProjeto}")
    else:
        print("Nenhum projeto a processar.")

if __name__ == "__main__":
    process()