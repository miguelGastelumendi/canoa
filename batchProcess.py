# -*- encoding: utf-8 -*-
import time
import apps.home.dbquery as dbquery
from apps.home.updateProjectDataSQL import sqls
from apps.config import Config
import apps.home.XLSXHelper as XLSXHelper

config = Config()

def calculateFinancials(idProjeto: int):
    print(f"idProjeto: {idProjeto}")
    for key in sqls.keys():
        result = dbquery.executeSQL(sqls[key].replace('@idProjeto',str(idProjeto)))
        print(f"{key} ({result.rowcount})")

def process():
    while True:
        toProcess = dbquery.getDataframeResultset("select * from listaAProcessar order by id")
        if len(toProcess) > 0:
            for _, row in toProcess.iterrows():
                emailEnvioResultado = dbquery.getValues(f'select emailEnvioResultado from Projeto where id = {row.idProjeto}')
                if emailEnvioResultado is None: # Usuário ainda não informou o email: esperar o próximo loop
                    continue
                idProjeto = row.idProjeto

                #idProjeto = 437

                calculateFinancials(idProjeto)
                XLSXHelper.GenerateXLSX(idProjeto)
                dbquery.executeSQL(f"delete from listaAProcessar where idProjeto = {row.idProjeto}")
        else:
            print("Nenhum projeto a processar.")
        time.sleep(60)

if __name__ == "__main__":
    process()