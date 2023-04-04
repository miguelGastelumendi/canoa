# -*- encoding: utf-8 -*-
import openpyxl
from openpyxl.worksheet.table import Table, TableStyleInfo
import apps.home.dbquery as dbquery
import math
import apps.home.XLSXHelperSQL as XLSXHelperSQL
from copy import copy

colName = lambda i: i >= 0 and colName(math.floor(i / 26 - 1)) + chr(int(round(65 + i % 26))) or ''

def rowColIndex(cName : str) -> int:
    index = 0
    cName = cName.replace('$', '')
    for i, n in enumerate(reversed([ord(c)-64 for c in cName if c >= 'A' and c <= 'Z'])):
        index += 26**i - 1 + n
    return int(cName[i + 1:]) + 1, index

class XLSXHelper:
    def __init__(self, templateFileName: str, idProjeto: int):
        self.xlsx = openpyxl.load_workbook(templateFileName)
        self.idProjeto = idProjeto

    def getUserNameDescProjeto(self):
        return dbquery.getDictFieldNamesValuesResultset(XLSXHelperSQL.SQLs['userNameDescProjeto'].format(self.idProjeto))

    def getDataAsRows(self, name: str):
        return dbquery.executeSQL(XLSXHelperSQL.SQLs[name].format(self.idProjeto))

    def getDataAsDict(self, name: str):
        return dbquery.getDictFieldNamesValuesResultset(XLSXHelperSQL.SQLs[name].format(self.idProjeto))

    def fillWorksheetFromRows(self, wsName: str, tbName: str, queryName = None):
        if queryName is None:
            queryName = wsName
        rows = self.getDataAsRows(queryName)
        ws = self.xlsx[wsName]
        if tbName not in self.xlsx.defined_names: # so, it's table
            initColName = ws.tables[tbName].ref[0:ws.tables[tbName].ref.index(':')]
        else:
            initColName = self.xlsx.defined_names['TxDsc'].value.split('!')[1]

        initRowNum, initColNum = rowColIndex(initColName)
        for i, row in enumerate(rows, initRowNum):
            for j, value in enumerate(row, initColNum):
                if ws.cell(1, j).has_style:
                    ws.cell(i, j).number_format = copy(ws.cell(1, j).number_format)
                ws.cell(i, j).value = value
            j += 1
            while ws.cell(2, j).value is not None:
                ws.cell(i, j).value = ws.cell(2, j).value
                if ws.cell(1, j).has_style:
                    ws.cell(i, j).number_format = copy(ws.cell(1, j).number_format)
                j += 1
        if not tbName in self.xlsx.defined_names:
            # recreating Table in worksheet
            tab = Table(displayName=tbName,
                        ref=f"{initColName}:{colName(j - 2)}{i}",
                        tableStyleInfo=ws.tables[tbName].tableStyleInfo)
            del ws.tables[tbName]
            ws.tables.add(tab)

    def fillWorksheetFromDict(self, name : str):
        dict = self.getDataAsDict(name)
        for key, value in dict.items():
            worksheet, cell = self.xlsx.defined_names[key].value.split('!')
            self.xlsx[worksheet][cell] = value

    def execute(self):
        self.fillWorksheetFromDict('Identificação')
        self.fillWorksheetFromRows('Silvicultura', 'tbSilv')
        self.fillWorksheetFromRows('Receitas', 'tbRec')
        self.fillWorksheetFromRows('Parametros', 'tbUnid', queryName='Unidades')
        self.fillWorksheetFromRows('Parametros', 'tbFaixa', queryName='Faixas')
        self.fillWorksheetFromRows('Parametros', 'TxDsc', queryName='txDsc')
        self.fillWorksheetFromRows('ResumoSilvicultura', 'tbResumo')
        self.fillWorksheetFromRows('FluxoCaixaFaixa', 'tbFcFaixa')
        self.fillWorksheetFromRows('Distribuição', 'tbDistribuicao', queryName='tbDistribuicao')

    def save(self):
        data = self.getUserNameDescProjeto()
        fname = f"doc/ResultadosReflorestaSP_{data['username'].replace(' ', '_')}_{data['descProjeto'].replace(' ', '_')}.xlsx"
        self.xlsx.save(fname)


def GenerateXLSX(idProjeto: int):
    xlsHelper = XLSXHelper('doc/TemplatePlanilhaComProjetoDoUsuario.xlsx', idProjeto)
    xlsHelper.execute()
    xlsHelper.save()
    pass
