import pandas as pd
from apps.home.dbquery import getDataframeResultset
from PIL import Image, ImageDraw, ImageFont, ImageColor

FaixaColors = {
    'Verde':   (196, 255, 14),
    'Marrom':  (185, 122, 86),
    'Laranja': (255, 127, 39),
    'Branca':  (255, 255, 255),
    'Roxa':    (163, 73,164)
}

FaixaChars = {
    'bordadura':      'o',
    'madeireira':     'ם',
    'nao_madeireira': 'Υ',
    'diversidade':    'D'
}

black = ImageColor.getrgb('black')
white = ImageColor.getrgb('white')

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
    localGrupoLst = [ClassGrupo(Grupo=row[0], nomeGrupo=row[1], numColunasJuntas=row[2], numColunas=row[3])
                     for _, row in dfGrupo.iterrows()]
    return localGrupoLst

def getPlantDistribuiton(idProjeto : int)->(dict, pd.DataFrame):
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
    return DistDic, FaixaDic

def drawRectBorder(drawcontext, xy, outline=None, width=0):
    (x1, y1), (x2, y2) = xy
    points = (x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)
    drawcontext.line(points, fill=outline, width=width)

def drawStrips(img: Image, colors: []):
    draw = ImageDraw.Draw(img)
    leftBottom = (img.size[0]-1, img.size[1]-1)
    stripWidth = img.size[0] / len(colors)
    for i in range(len(colors)):
        draw.rectangle((0 + i * stripWidth, 0) + leftBottom,
                       fill=FaixaColors[colors[i]],
                       outline='black',
                       width=2)
    draw.text((1, 1), "Sample text", fill=black)


def drawPicPlantDistribution(DistDic: dict, fname: str, colors = ()):
    width = 600
    height = 800
    img = Image.new(mode="RGB", size=(width, height), color='white')
    drawStrips(img, colors=colors)
    img.show()
    pass

def createPlantDistributionArray(DistDict: dict, faixas: pd.DataFrame):
    pass
