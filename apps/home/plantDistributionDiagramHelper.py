import pandas as pd
from apps.home.dbquery import getDataframeResultset, getDictResultset
from PIL import Image, ImageDraw, ImageFont, ImageColor

FaixasTipoColors = {
    'Verde': (196, 255, 14),
    'Marrom': (185, 122, 86),
    'Laranja': (255, 127, 39),
    'Branca': (255, 255, 255),
    'Roxa': (163, 73, 164)
}

FaixasTipoChars = {
    'bordadura': 'o',
    'madeireira': 'ם',
    'nao_madeireira': 'Υ',
    'diversidade': 'D'
}

black = ImageColor.getrgb('black')
white = ImageColor.getrgb('white')


class ClassFaixasTipo(object):
    def __init__(self, nomeFaixasTipo: str, ColunasPorFaixasTipo: int, totalColunas: int):
        self.nomeFaixasTipo = nomeFaixasTipo
        self.ColunasPorFaixasTipo = ColunasPorFaixasTipo
        self.totalColunas = totalColunas


class ClassGrupo(object):
    def __init__(self, Grupo: int, nomeGrupo: str, numColunasJuntas: int, numColunas: int):
        self.Grupo = Grupo
        self.nomeGrupo = nomeGrupo
        self.numColunasJuntas = numColunasJuntas
        self.numColunas = numColunas

def getFaixas(idProjeto: int) -> pd.DataFrame:
    faixasQuery = f"""select ft.descFaixa from ModeloFaixa mf 
inner join ModeloPlantio mp 
on mf.idModeloPlantio = mp.id 
inner join FaixaTipo ft 
on mf.idFaixaTipo = ft.id 
inner join Projeto p 
on p.idModeloPlantio = mp.id
where p.id = {idProjeto}"""
    dfFaixasTipo = getDataframeResultset(faixasQuery)
    return dfFaixasTipo

def GetFaixasTipo(idProjeto: int) -> dict:
    # constroi o dic de FaixasTipos
    # FaixasTipos
    # --------
    localFaixasTipoQuery = 'select idFaixaTipo, nomeFaixa, ColunasPorFaixa, totalColunas ' \
                      f'from V_DistribuicaoFaixas where idProjeto = {idProjeto}'
    dfFaixasTipo = getDataframeResultset(localFaixasTipoQuery)
    localFaixasTipoDic = {row[0]: ClassFaixasTipo(nomeFaixasTipo=row[1], ColunasPorFaixasTipo=row[2], totalColunas=row[3])
                     for _, row in dfFaixasTipo.iterrows()}
    return localFaixasTipoDic


def GetGrupo(idProjeto: int, idFaixaTipo: int) -> list:
    localGrupoQuery = "select de.Grupo, de.nomeGrupo, de.numColunasJuntas," + \
                      "        round(sum((de.AreaOcupacao * df.QtdDeFaixas))/(100.00*cast(pm.EspEntreColunas as integer)),0) numColunas" + \
                      "   from V_DistribuicaoEspecies de " + \
                      "        inner join V_DistribuicaoFaixas df on df.idProjeto = de.idProjeto and df.idFaixaTipo = de.idFaixaTipo" + \
                      "        cross join (select ValorParametro as EspEntreColunas" + \
                      "                      from Parametro where nomeParametro = 'EspacamPadrao') pm" + \
                      f"  where de.idProjeto = {idProjeto}" + \
                      f"    and de.idFaixaTipo = {idFaixaTipo}" + \
                      "  group by de.idFaixaTipo, de.NomeFaixa, de.Grupo," \
                      "        de.nomeGrupo, de.numColunasJuntas, pm.EspEntreColunas" + \
                      "  order by de.Grupo"
    dfGrupo = getDataframeResultset(localGrupoQuery)
    localGrupoLst = [ClassGrupo(Grupo=row[0], nomeGrupo=row[1], numColunasJuntas=row[2], numColunas=row[3])
                     for _, row in dfGrupo.iterrows()]
    return localGrupoLst


def getPlantDistribuiton(idProjeto: int) -> (dict, dict, pd.DataFrame):
    ProxGrupo = 0
    DistDic = {}

    Faixas = getFaixas(idProjeto)

    FaixasTipoDic = GetFaixasTipo(idProjeto)
    for idFaixasTipo in FaixasTipoDic.keys():
        DistFaixasTipoDic = {}
        GrupoLst = GetGrupo(idProjeto, idFaixasTipo)
        numDeGrupos = len(GrupoLst)
        if numDeGrupos == 0:
            continue
        GrupoAtual = GrupoLst[ProxGrupo]
        DessaVez = 1
        numColuna = 1

        while numColuna < FaixasTipoDic[idFaixasTipo].totalColunas:

            while DessaVez <= GrupoAtual.numColunasJuntas and GrupoAtual.numColunas > 0:
                DistFaixasTipoDic[numColuna] = (GrupoAtual.Grupo, GrupoAtual.nomeGrupo)
                DessaVez += 1
                numColuna += 1
                GrupoAtual.numColunas = GrupoAtual.numColunas - 1

            DessaVez = 1
            ProxGrupo = + 1
            if ProxGrupo >= numDeGrupos:
                ProxGrupo = 0
            GrupoAtual = GrupoLst[ProxGrupo]

        DistDic[idFaixasTipo] = DistFaixasTipoDic
    return DistDic, FaixasTipoDic, Faixas

def drawStrips(FaixasTipos: dict, Faixas):
    width = 800
    height = 800
    colNamesHeight = 10
    verticalInterval = 10
    img = Image.new(mode="RGB", size=(width, height), color='white')
    draw = ImageDraw.Draw(img)
    leftBottom = (img.size[0] - 1, img.size[1] - 1)
    stripWidth = img.size[0] / len(Faixas)
    i = 0
    for i in range(len(Faixas)):
        draw.rectangle((i * stripWidth, colNamesHeight + verticalInterval) + leftBottom,
                       fill='white',
                       outline='black',
                       width=2)
        draw.rectangle((i * stripWidth, colNamesHeight + verticalInterval) + leftBottom,
                       fill=FaixasTipoColors[Faixas.iloc[i][0]],
                       outline='black',
                       width=2)

    draw.text((1, 1), "Sample text", fill=black)
    return img


def drawPicPlantDistribution(DistDic: dict, fname: str, FaixasTipos: dict, Faixas: pd.DataFrame):
    img = drawStrips(FaixasTipos, Faixas)
    img.show()
    pass


def createPlantDistributionArray(DistDict: dict, FaixasTipos: pd.DataFrame, Faixas: pd.DataFrame):
    pass
