# -*- encoding: utf-8 -*-
import time
import apps.home.dbquery as dbquery
from apps.home.updateProjectDataSQL import sqls
from apps.config import Config
import apps.home.XLSXHelper as XLSXHelper
import argparse

config = Config()

def ProcessCmdLine():
    parser = argparse.ArgumentParser(description='SISMOI import data app.')
    parser.add_argument('-pi', '--project_id', help='Id of the project to process', type=int, default=-1)
    return parser.parse_args()

def calculateFinancials(idProjeto: int):
    for key in sqls.keys():
        result = dbquery.executeSQL(sqls[key].replace('@idProjeto',str(idProjeto)))
        print(f"{key} ({result.rowcount})")

def process():
    args = ProcessCmdLine()
    while True:
        if args.project_id == -1:
            toProcess = dbquery.getDataframeResultset("select * from listaAProcessar order by id")
        else:
            toProcess = dbquery.getDataframeResultset(f"select {args.project_id} as idProjeto")
        if len(toProcess) > 0:
            for _, row in toProcess.iterrows():
                idProjeto = row.idProjeto
                print(f"idProjeto: {idProjeto}")
                emailEnvioResultado = dbquery.getValues(f'select emailEnvioResultado from Projeto where id = {idProjeto}')
                if emailEnvioResultado is None: # Usuário ainda não informou o email: esperar o próximo loop
                    print('Ainda sem email de envio')
                    continue

                #idProjeto = 437

                calculateFinancials(idProjeto)
                XLSXHelper.GenerateXLSX(idProjeto)
                dbquery.executeSQL(f"delete from listaAProcessar where idProjeto = {row.idProjeto}")
        else:
            print("Nenhum projeto a processar.")
        time.sleep(60)

if __name__ == "__main__":
    process()