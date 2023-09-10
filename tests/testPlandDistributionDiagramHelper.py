from apps.home.plantDistributionDiagramHelper import getPlantDistribuiton, createPlantDistributionArray, drawPicPlantDistribution

if __name__ == '__main__':
    projectId = 442
    dist, FaixasTipos, Faixas = getPlantDistribuiton(projectId)

    createPlantDistributionArray(dist, FaixasTipos, Faixas)
    drawPicPlantDistribution(dist, '', FaixasTipos, Faixas)
    pass