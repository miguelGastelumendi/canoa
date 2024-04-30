# -*- encoding: utf-8 -*-
import time
import apps.home.dbquery as dbquery
from apps.home.updateProjectDataSQL import sqls
from apps.config import Config
import apps.home.XLSXHelper as XLSXHelper
import argparse
import apps.caatinga.logHelper as logHelper

config = Config()


def ProcessCmdLine():
    parser = argparse.ArgumentParser(description='ReflorestaSP Pos-processing.')
    parser.add_argument('-pi', '--project_id', help='Id of the project to process', type=int, default=-1)
    parser.add_argument('-d', '--debug', type=int, default=0)
    parser.add_argument('-lf', '--logfile', type=str, default='')
    return parser.parse_args()


def calculateFinancials(idProjeto: int, debug: int, log: logHelper.Log):
    for key in sqls.keys():
        try:
            sql = sqls[key].replace('@idProjeto', str(idProjeto))
            result = dbquery.executeSQL(sql)
            print(f"{key} ({result.rowcount})")
            if debug == 1:
                log.log(sql)
        except Exception as e:
            log.log(f'\nErro na query acima: {e}')

def process():
    toProcess = None
    args = ProcessCmdLine()
    if args.logfile != '':
        log = logHelper.Log(args.logfile)
    else:
        log = logHelper.Log('')  # log to screen only
    try:
        toProcess = dbquery.getDataframeResultset("select * from listaAProcessar where 1=0") # ?
    except Exception as e:
        log.log(e)
        print(e)
        exit
    while True:
        try:
            if args.project_id == -1 and len(toProcess) == 0:
                toProcess = dbquery.getDataframeResultset("select * from listaAProcessar order by id")
            else:
                toProcess = dbquery.getDataframeResultset(f"select {args.project_id} as idProjeto")
            log.log(f'lista com {len(toProcess)} a processar.')
            if len(toProcess) > 0:
                while len(toProcess) > 0:
                    row = toProcess.iloc[0]
                    idProjeto = row.idProjeto
                    log.log(f"idProjeto: {idProjeto}")
                    emailEnvioResultado = dbquery.getValues(
                        f'select emailEnvioResultado from Projeto where id = {idProjeto}')
                    if emailEnvioResultado is None:  # Usuário ainda não informou o email: esperar o próximo loop
                        print('Ainda sem email de envio')
                        continue

                    calculateFinancials(idProjeto, args.debug, log)
                    log.log('Iniciando geração da planilha')
                    XLSXHelper.GenerateXLSX(idProjeto, log)
                    toProcess = toProcess[toProcess['idProjeto'] != idProjeto]
                    dbquery.executeSQL(f"delete from listaAProcessar where idProjeto = {row.idProjeto}")
            time.sleep(60)
        except Exception as e:
            log.log(e)
            print(e)
            if toProcess is not None:
                toProcess = toProcess[toProcess['idProjeto'] != idProjeto]
            #dbquery.executeSQL(f"delete from listaAProcessar where idProjeto = {row.idProjeto}")

if __name__ == "__main__":
    process()
