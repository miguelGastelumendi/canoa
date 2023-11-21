import pandas as pd
from apps.home.dbquery import getDataframeResultset, getDictResultset
from PIL import Image, ImageDraw, ImageFont, ImageColor

class FaixasTipo(object):
    def __init__(self, nomeFaixasTipo: str, ColunasPorFaixasTipo: int, totalColunas: int):
        self.width = 800
        self.height = 700
        self.colNamesHeight = 10
        self.verticalInterval = 10
        self.nomeFaixasTipo = nomeFaixasTipo
        self.ColunasPorFaixasTipo = ColunasPorFaixasTipo
        self.totalColunas = totalColunas
        self.img: Image
        self.draw: ImageDraw

class Grupo(object):
    def __init__(self, Grupo: int, nomeGrupo: str, numColunasJuntas: int, numColunas: int):
        self.Grupo = Grupo
        self.nomeGrupo = nomeGrupo
        self.numColunasJuntas = numColunasJuntas
        self.numColunas = numColunas
class Diagram(object):
    def __init__(self, idProjeto: int):

        self.idProjeto = idProjeto

        self.FaixasTipoColors = {
            'Verde': (196, 255, 14),
            'Marrom': (185, 122, 86),
            'Laranja': (255, 127, 39),
            'Branca': (255, 255, 255),
            'Roxa': (163, 73, 164)
        }

        self.FaixasTipoChars = {
            'bordadura': 'o',
            'madeireira': 'ם',
            'nao_madeireira': 'Υ',
            'diversidade': 'D'
        }
        self.black = ImageColor.getrgb('black')
        self.white = ImageColor.getrgb('white')


    def getFaixas(self, idProjeto: int) -> pd.DataFrame:
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

    def GetFaixasTipo(self, idProjeto: int) -> dict:
        # constroi o dic de FaixasTipos
        # FaixasTipos
        # --------
        localFaixasTipoQuery = 'select idFaixaTipo, nomeFaixa, ColunasPorFaixa, totalColunas ' \
                          f'from V_DistribuicaoFaixas where idProjeto = {idProjeto}'
        dfFaixasTipo = getDataframeResultset(localFaixasTipoQuery)
        localFaixasTipoDic = {row[0]: FaixasTipo(nomeFaixasTipo=row[1], ColunasPorFaixasTipo=row[2], totalColunas=row[3])
                         for _, row in dfFaixasTipo.iterrows()}
        return localFaixasTipoDic


    def GetGrupo(self, idProjeto: int, idFaixaTipo: int) -> list:
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
        localGrupoLst = [Grupo(Grupo=row[0], nomeGrupo=row[1], numColunasJuntas=row[2], numColunas=row[3])
                         for _, row in dfGrupo.iterrows()]
        return localGrupoLst


    def getPlantDistribuiton(self):
        ProxGrupo = 0
        self.DistDic = {}

        self.Faixas = self.getFaixas(self.idProjeto)

        self.FaixasTipoDic = self.GetFaixasTipo(self.idProjeto)
        for idFaixasTipo in self.FaixasTipoDic.keys():
            DistFaixasTipoDic = {}
            GrupoLst = self.GetGrupo(self.idProjeto, idFaixasTipo)
            numDeGrupos = len(GrupoLst)
            if numDeGrupos == 0:
                continue
            GrupoAtual = GrupoLst[ProxGrupo]
            DessaVez = 1
            numColuna = 1

        while numColuna < self.FaixasTipoDic[idFaixasTipo].totalColunas:

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

        self.DistDic[idFaixasTipo] = DistFaixasTipoDic

        def drawStrips(self, FaixasTipos: dict, Faixas):

            self.img = Image.new(mode="RGB", size=(self.width, self.height), color='white')
            self.draw = ImageDraw.Draw(self.img)
            leftBottom = (self.img.size[0] - 1, self.img.size[1] - 1)
            stripWidth = self.img.size[0] / len(Faixas)
            i = 0
            for i in range(len(Faixas)):
                self.draw.rectangle((i * stripWidth, self.colNamesHeight + self.verticalInterval) + leftBottom,
                               fill='white',
                               outline='black',
                               width=2)
                self.draw.rectangle((i * stripWidth, self.colNamesHeight + self.verticalInterval) + leftBottom,
                               fill=self.FaixasTipoColors[Faixas.iloc[i][0]],
                               outline='black',
                               width=2)

    def drawTrees(self, img: Image, DistDic: dict, fname: str, Faixas: pd.DataFrame):
        self.draw.text((1, 1), "Sample text", fill=self.black)
        pass


    def drawPicPlantDistribution(self, DistDic: dict, fname: str, FaixasTipos: dict, Faixas: pd.DataFrame):
        self.drawStrips(FaixasTipos, Faixas)
        self.img.show()
        pass

    def createImage(self):
        self.getPlantDistribuiton(self)
