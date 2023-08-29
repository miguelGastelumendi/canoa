# -*- encoding: utf-8 -*-
import time
import apps.home.dbquery as dbquery
from apps.home.updateProjectDataSQL import sqls
from apps.config import Config
import apps.home.XLSXHelper as XLSXHelper
import argparse

config = Config()

def ProcessCmdLine():
    parser = argparse.ArgumentParser(description='ReflorestaSP Pos-processing.')
    parser.add_argument('-pi', '--project_id', help='Id of the project to process', type=int, default=-1)
    parser.add_argument('-d', '--debug', type=int, default=0)
    return parser.parse_args()

def calculateFinancials(idProjeto: int, debug: int):
    for key in sqls.keys():
        sql = sqls[key].replace('@idProjeto',str(idProjeto))
        result = dbquery.executeSQL(sql)
        print(f"{key} ({result.rowcount})")
        if (debug == 1):
            print(sql)
            print()

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

                calculateFinancials(idProjeto, args.debug)
                XLSXHelper.GenerateXLSX(idProjeto)
                dbquery.executeSQL(f"delete from listaAProcessar where idProjeto = {row.idProjeto}")
        else:
            print("Nenhum projeto a processar.")
        time.sleep(60)

if __name__ == "__main__":
    process()