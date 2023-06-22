from apps.home.plantDistributionDiagramHelper import getPlantDistribuiton, createPlantDistributionArray, drawPicPlantDistribution
from apps.home.dbquery import getDataframeResultset

if __name__ == '__main__':
    projectId = 390
    dist, faixas=getPlantDistribuiton(projectId)

    createPlantDistributionArray(dist, faixas)
    drawPicPlantDistribution(dist, '', faixas)
    pass