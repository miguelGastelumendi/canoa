
from sqlalchemy import create_engine
import pandas as pd
from spComp import GlobalVar
import os


class ClassLane(object):
    def __init__(self, laneColor: str, laneSize: int):
        self.laneColor = laneColor
        self.laneSize = laneSize

class ClassCompToDo(object):
    def __init__(self,  ecoReg: int, ecoFisio: int):
        self.ecoReg = ecoReg
        self.ecoFisio = ecoFisio

class ClassSpecies(object):
    def __init__(self, spId: int, indSpace: int, maxQttInd: int, spIndRanking: float ):
        self.spId = spId
        self.indSpace = indSpace
        self.maxQttInd = maxQttInd
        self.spRanking = spIndRanking

class ClassCompItem(object):
    def __init__(self, spId: int, spOrder: int, spKey: str, spQtt: int, spTotSpace: int, spTotRanking: float):
        self.spId = spId
        self.spOrder = spOrder
        self.spKey = spKey
        self.spQtt = spQtt
        self.spTotSpace = spTotSpace
        self.spTotRanking = spTotRanking

class ClassComposition(object):
    def __init__(self, seqStr: str, cpTotRanking: float, cpTotQtt: int, filledSpace: int, compItemLst: list ):
        self.seqStr = seqStr
        self.cpTotRanking = cpTotRanking
        self.cpTotQtt = cpTotQtt
        self.filledSpace = filledSpace
        self.compItemLst = compItemLst

def connectToSql():

    # Create the database engine
    engine = create_engine(os.environ['SQLALCHEMY_DATABASE_URI'])
    return engine

def GetParameter(engine, prmName):
    localValue : int = 0
    if prmName == 'QtdCombinacoes':
        localValue: int = 0
        localQuery = "select valorParametro from Parametro where nomeParametro = '" + prmName + "'"
        df = pd.read_sql_query(localQuery, engine)
        localValue = int(df.loc[0, 'valorParametro'])
    return localValue

def GetData(engine) -> (dict, dict):
    # build the dictionary of lanes
    #-------------------------------
    localLaneDic = dict()
    localLaneQuery = 'select id, nomeFaixa, AreaFaixa from vwFaixaTipo'
    dfLane = pd.read_sql_query(localLaneQuery, engine)
    localLaneDic = {row[0]: ClassLane(laneColor=row[1], laneSize=row[2]) for _, row in dfLane.iterrows()}
    # build the dictionary of Eco-Fisio compositions to do
    #-----------------------------------------------------
    localToDoDic = dict()
    # -- teste erro
    localToDoQuery = 'select distinct f.idFaixaTipo, a.idRegiaoEco, a.idFitoFisionomia ' +\
                     '  from adaptacao a ' +\
                     '       inner join FitoFisionomia ff on ff.id = a.idFitoFisionomia ' +\
                     '       inner join (select distinct mp.idFormacao, mf.idFaixaTipo ' +\
                     '                     from ModeloPlantio mp ' +\
                     '                          inner join ModeloFaixa mf on mf.idModeloPlantio = mp.id ' +\
				     '                          inner join vwFaixaTipo ft   on ft.id = mf.idFaixaTipo ) f ' +\
		             '          on f.idFormacao = ff.idFormacao ' +\
                     ' order by f.idFaixaTipo, a.idFitoFisionomia, a.idRegiaoEco '
    dfToDo = pd.read_sql_query(localToDoQuery, engine)
    for lane in localLaneDic.keys():
        ToDoLst = list()
        ToDoLst = [ClassCompToDo(ecoReg=row[1], ecoFisio=row[2]) for _, row in dfToDo.iterrows() if row[0] == lane]
        localToDoDic[lane] = [x for x in ToDoLst]
    # build the dictionary of Eco-Fisio compositions to do
    #-----------------------------------------------------
    localSpeciesDic = dict()
    localSpeciesQuery = 'select v.idFaixaTipo, v.idFitoFisionomia, v.idRegiaoEco, v.idEspecie, ' +\
                        '       v.areaOcupacao, v.numMaxIndFx, v.Ranking ' +\
                        '  from V_ParaMontarCombinacoes v '
    dfSpecies = pd.read_sql_query(localSpeciesQuery, engine)
    for lane in localLaneDic.keys():
        for toDo in localToDoDic[lane]:
            SpeciesLst = list()
            SpeciesLst = [ClassSpecies(spId=row[3],indSpace=row[4],maxQttInd=row[5],spIndRanking=row[6]) \
                          for _,row in dfSpecies.iterrows() \
                          if row[0] == lane and \
                             row[1] == toDo.ecoFisio and \
                             row[2] == toDo.ecoReg]
            localSpeciesDic[(lane, toDo.ecoFisio, toDo.ecoReg)] = [x for x in SpeciesLst]

    return (localLaneDic,localToDoDic,localSpeciesDic)

def DeleteCompositions(engine) -> int:
    dbError: int = 0
    localSql : str = ''
    localSql = "delete from CombinaEspecie where id > 0; " +\
               "delete from Combinacao where id > 0; " + \
               "DBCC CHECKIDENT ('CombinaEspecie', RESEED, 0) ; "+\
               "DBCC CHECKIDENT ('Combinacao', RESEED, 0) ; "

    with engine.connect() as conn:
        dbResult = conn.execute(localSql)
    # descobrir com ver se deu erro, fazer try - exception
    return dbError

def spSequence(max) -> list:
    seqLst = []
    seqLst = [f'{i:03}' for i in range(1, max + 1)]
    return seqLst

def SortSpecies(speciesLst, spSeq) -> dict:
    localDic = {}
    sortedLst = sorted(speciesLst, key=lambda x: x.spRanking, reverse=True)
    s = 0
    for spItem in sortedLst:
        localDic[spSeq[s]] = spItem
        s += 1
    return localDic

def SaveCompositions(engine, localCpCount, lane, ecoFisio, ecoReg, compositionLst: list) -> int:

    cpOrder: int = 0
    for cpItem in compositionLst:
        localCpCount += 1
        cpOrder += 1
        newRow = {
            'GrupoCombinacao': int(cpOrder),
            'idFaixaTipo': int(lane),
            'idFitoFisionomia': int(ecoFisio),
            'idRegiaoEco': int(ecoReg),
            'numArvTotal': int(cpItem.cpTotQtt),
            'Ranking': cpItem.cpTotRanking,
            'Ocupacao': int(cpItem.filledSpace)
        }
        localCpDf = pd.DataFrame([newRow])
        GlobalVar.dfComposition = pd.concat([GlobalVar.dfComposition, localCpDf], ignore_index=True)

        for spItem in cpItem.compItemLst:
            newRow = {
                'idCombinacao': int(localCpCount),
                'idEspecie': int(spItem.spId),
                'numArvores': int(spItem.spQtt),
                'Ranking': spItem.spTotRanking,
                'areaOcupacao': spItem.spTotSpace,
                'Ordem': int(spItem.spOrder)}
            localSpDf = pd.DataFrame([newRow])
            GlobalVar.dfSpecies = pd.concat([GlobalVar.dfSpecies, localSpDf], ignore_index=True)
    return localCpCount

def InsertIntoSQL(engine):
    tableName = 'Combinacao'
    GlobalVar.dfComposition.to_sql(tableName, con=engine, if_exists='append', index=False)

    tableName = 'CombinaEspecie'
    GlobalVar.dfSpecies.to_sql(tableName, con=engine, if_exists='append', index=False)




