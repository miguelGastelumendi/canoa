# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import spData as db
import spCompBuild as cp
import pandas as pd
from datetime import datetime

class GlobalVar(object):
    dfComposition = pd.DataFrame()
    dfSpecies = pd.DataFrame()

def InitGV():
    cpList = [{'GrupoCombinacao': 0, 'idFaixaTipo': 0, 'idFitoFisionomia': 0, 'idRegiaoEco': 0, 'numArvTotal': 0,
               'Ranking': 0.1, 'Ocupacao': 0.1}]
    GlobalVar.dfComposition = pd.DataFrame([cpList])

    spList = [{'idCombinacao': 0, 'idEspecie': 0, 'numArvores': 0, 'Ranking': 0.1, 'areaOcupacao': 0.1, 'Ordem': 0}]
    GlobalVar.dfSpecies = pd.DataFrame([spList])

def printLst(nameLst, cpLst):
    print(nameLst)
    for cpItem in cpLst:
        print(cpItem)

def printCurrentTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # initialize control variables
    printCurrentTime()
    cpCount = 0
    lenCpLst: int = 0
    qttCpParam: int = 0
    laneId: int = 0
    # initialize lists and dics
    speciesLst = []
    lanesDic = {}
    compToDoDic = {}
    AllSpeciesDic = {}
    speciesDic = {}
    # get all the data needed to the process
    engine = db.connectToSql()
    spSeq = db.spSequence(200)
    qttCpParam = db.GetParameter(engine, 'QtdCombinacoes')
    (lanesDic, compToDoDic, AllSpeciesDic) = db.GetData(engine)
    # initialize insert structure
    InitGV()

    # try to delete old compositions, if no errors: continue
    if db.DeleteCompositions(engine) == 0:
        for laneId in lanesDic.keys():
            print('laneId= '+str(laneId))
            compToDoLst = []
            compToDoLst = compToDoDic[laneId]

            for cpToDoItem in compToDoLst:
                print('Fisio= ' + str(cpToDoItem.ecoFisio) + 'REco= '+ str(cpToDoItem.ecoReg))
                compositionLst = []
                speciesLst = AllSpeciesDic[(laneId, cpToDoItem.ecoFisio, cpToDoItem.ecoReg)]
                if len(speciesLst) > 0:
                   speciesDic = db.SortSpecies(speciesLst, spSeq)
                   MainSpLst = []
                   MainSpLst = [x for x in speciesDic.keys()]

                   takeOffLst = []
                   takeOffLst = cp.BuildTakeOff(lanesDic[laneId].laneSize, speciesDic)

                   ModifiedSpLst = []
                   ModifiedSpLst = [x for x in MainSpLst]
                   # compSetLst is a list of Composition
                   compSetLst = []
                   if len(ModifiedSpLst) >= 1:
                        compSetLst = cp.BuildCompSet(lanesDic[laneId].laneSize, ModifiedSpLst, speciesDic)
                        compositionLst = compositionLst + compSetLst
                        compSetLst = []
                   for takeOffItem in takeOffLst:
                        # melhorar o tekeOff Lst para ter mais combinações
                        ModifiedSpLst = [x for x in MainSpLst if x != takeOffItem]
                        if len(ModifiedSpLst) >= 1:
                            compSetLst = cp.BuildCompSet(lanesDic[laneId].laneSize, ModifiedSpLst, speciesDic)
                            # add only compositions that are not yet in the composition list
                            compositionLst = cp.AddCompSet(compositionLst, compSetLst)
                            compSetLst = []
                        else:
                            break
                   #end for takeOff
                   #------------------------------------------rank compositionLst
                   compositionLst.sort(key=lambda x: x.cpTotRanking, reverse=True)
                   #--------------------------------choose the best x composition
                   lenCpLst = len(compositionLst)
                   if lenCpLst > qttCpParam:
                       del compositionLst[qttCpParam+1:lenCpLst]
                   #---------------------------------------------save composition
                   cpCount = db.SaveCompositions(engine, cpCount, laneId, cpToDoItem.ecoFisio, cpToDoItem.ecoReg, compositionLst)
                   print('cpCount = ', str(cpCount))
            #end for cpToDoItem
        #end for laneId
        printCurrentTime()
        print('Inserting into the database')
        db.InsertIntoSQL(engine)

    printCurrentTime()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
