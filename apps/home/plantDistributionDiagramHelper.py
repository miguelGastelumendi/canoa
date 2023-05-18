import pandas as pd
from apps.home.dbquery import getDataframeResultset

class ClassFaixa(object):
    def __init__(self, nomeFaixa: str, ColunasPorFaixa: int, totalColunas: int):
        self.nomeFaixa = nomeFaixa
        self.ColunasPorFaixa = ColunasPorFaixa
        self.totalColunas = totalColunas

class ClassGrupo(object):
    def __init__(self, Grupo:int, nomeGrupo: str, numColunasJuntas: int, numColunas: int):
        self.Grupo = Grupo
        self.nomeGrupo = nomeGrupo
        self.numColunasJuntas = numColunasJuntas
        self.numColunas = numColunas

def GetFaixa(idProjeto: int) -> dict:
    # constroi o dic de faixas
    # faixas
    #--------
    localFaixaQuery = 'select idFaixaTipo, nomeFaixa, ColunasPorFaixa, totalColunas ' \
                     f'from V_DistribuicaoFaixas where idProjeto = {idProjeto}'
    dfFaixa = getDataframeResultset(localFaixaQuery)
    localFaixaDic = {row[0]: ClassFaixa(nomeFaixa=row[1], ColunasPorFaixa=row[2], totalColunas=row[3])
                     for _, row in dfFaixa.iterrows()}
    return localFaixaDic

def GetGrupo(idProjeto: int, idFaixaTipo: int) -> list:
    localGrupoQuery = "select de.Grupo, de.nomeGrupo, de.numColunasJuntas, " +\
                     "        round(sum((de.AreaOcupacao * df.QtdDeFaixas))/(100.00*cast(pm.EspEntreColunas as integer)),0) numColunas "  +\
                     "   from V_DistribuicaoEspecies de "  +\
                     "        inner join V_DistribuicaoFaixas df on df.idProjeto = de.idProjeto and df.idFaixaTipo = de.idFaixaTipo "  +\
                     "        cross join (select ValorParametro as EspEntreColunas "  +\
                     "                      from Parametro where nomeParametro = 'EspacamPadrao') pm "  +\
                     f"  where de.idProjeto = {idProjeto}" +\
                     f"    and de.idFaixaTipo = {idFaixaTipo}" +\
                     "  group by de.idFaixaTipo, de.NomeFaixa, de.Grupo, " \
                     "        de.nomeGrupo, de.numColunasJuntas, pm.EspEntreColunas " +\
                     "  order by de.Grupo "
    dfGrupo = getDataframeResultset(localGrupoQuery)
    localGrupoLst = [ClassGrupo(Grupo=row[0], nomeGrupo=row[1], numColunasJuntas=row[2], numColunas=row[3]) for _, row in dfGrupo.iterrows()]
    return localGrupoLst

def getPlantDistribuiton(idProjeto : int)->dict:
    ProxGrupo = 0
    DistDic = {}

    FaixaDic = GetFaixa(idProjeto)
    for idFaixa in FaixaDic.keys():
        DistFaixaDic = {}
        GrupoLst = GetGrupo(idProjeto, idFaixa)
        numDeGrupos = len(GrupoLst)
        GrupoAtual = GrupoLst[ProxGrupo]
        DessaVez = 1
        numColuna = 1

        while numColuna < FaixaDic[idFaixa].totalColunas:

            while DessaVez <= GrupoAtual.numColunasJuntas and GrupoAtual.numColunas > 0:
               DistFaixaDic[numColuna] = (GrupoAtual.Grupo, GrupoAtual.nomeGrupo)
               DessaVez += 1
               numColuna += 1
               GrupoAtual.numColunas = GrupoAtual.numColunas - 1

            DessaVez = 1
            ProxGrupo =+ 1
            if ProxGrupo >= numDeGrupos:
               ProxGrupo = 0
            GrupoAtual = GrupoLst[ProxGrupo]

        DistDic[idFaixa] = DistFaixaDic
    return DistDic