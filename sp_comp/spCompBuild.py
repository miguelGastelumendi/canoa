import spData as db
import math


def BuildTakeOff(laneSize, speciesDic) -> list:
    localLst = []
    sortedKeys = []
    laneFilled: int = 0
    spKey: str = 'X'

    sortedKeys = sorted(speciesDic.keys())

    for spKey in sortedKeys:
        laneFilled = laneFilled + (speciesDic[spKey].indSpace * speciesDic[spKey].maxQttInd)
        localLst.append((spKey))
        if laneFilled >= laneSize:
            break
    # falta combinar de 2 em 2
    return localLst

def MaxSpaceSpLst(spLst,speciesDic) -> int:
    TotMaxSpace: int = 0
    for spItem in spLst:
        TotMaxSpace += speciesDic[spItem].indSpace * speciesDic[spItem].maxQttInd
    return TotMaxSpace

def BuildCompSet(laneSize, spLst, speciesDic) -> list:
    localCompLst = []
    composition = db.ClassComposition(seqStr='', cpTotRanking=0.000001, cpTotQtt=0, filledSpace=0, compItemLst=[])

    compItemLst = []
    cpItem = db.ClassCompItem(spId=0, spOrder=0, spKey='', spQtt=0, spTotSpace=0, spTotRanking= 0.00001)

    laneFilled: int = 0
    remainingSpace: int = 0
    spKey: str = 'X'
    spQtt: int = 0
    spOrder: int = 0
    spString: str = ''
    spTotRanking: float = 0.0
    spTotQtt: int = 0

    spLst = sorted(spLst)
    while True:
        for spKey in spLst:
            remainingSpace = laneSize - laneFilled
            if remainingSpace >= speciesDic[spKey].indSpace :
                if (speciesDic[spKey].indSpace * speciesDic[spKey].maxQttInd) <= remainingSpace:
                    spQtt = speciesDic[spKey].maxQttInd
                    laneFilled += speciesDic[spKey].indSpace * spQtt
                else:
                    spQtt = math.floor(remainingSpace / speciesDic[spKey].indSpace)
                    laneFilled += speciesDic[spKey].indSpace * spQtt

                if spQtt > 0:
                    spOrder += 1
                    cpItem.spId = speciesDic[spKey].spId
                    cpItem.spOrder = spOrder
                    cpItem.spKey = spKey
                    cpItem.spQtt = spQtt
                    cpItem.spTotSpace = speciesDic[spKey].indSpace * spQtt
                    cpItem.spTotRanking = speciesDic[spKey].spRanking * spQtt
                    compItemLst.append(db.ClassCompItem(spId=cpItem.spId,
                                                        spOrder=cpItem.spOrder,
                                                        spKey=cpItem.spKey,
                                                        spQtt=cpItem.spQtt,
                                                        spTotSpace=cpItem.spTotSpace,
                                                        spTotRanking=cpItem.spTotRanking))
                    spString += spKey
                    spTotRanking += speciesDic[spKey].spRanking * spQtt
                    spTotQtt += spQtt
                    lastSpKey = spKey
            else:
                break
        composition.seqStr = spString
        composition.cpTotRanking = spTotRanking
        composition.cpTotQtt = spTotQtt
        composition.filledSpace = laneFilled
        composition.compItemLst = compItemLst
        localCompLst.append(db.ClassComposition(seqStr=composition.seqStr,
                                                cpTotRanking=composition.cpTotRanking,
                                                cpTotQtt=composition.cpTotQtt,
                                                filledSpace=composition.filledSpace,
                                                compItemLst=composition.compItemLst))
        spLst.remove(lastSpKey)
        if MaxSpaceSpLst(spLst, speciesDic) < laneSize:
            break
        spOrder = 0
        spString = ''
        spTotRanking = 0
        spTotQtt = 0
        laneFilled = 0
        compItemLst = []
    # end while True

    return localCompLst
#end BuildCompSet

def AddCompSet(compositionLst,compSetLst) -> list:
    seqStrLst = []
    newCompSet = []
    seqStrLst = [x.seqStr for x in compositionLst]
    newCompSet = [x for x in compSetLst if x.seqStr not in seqStrLst]
    compositionLst = compositionLst + newCompSet
    return compositionLst