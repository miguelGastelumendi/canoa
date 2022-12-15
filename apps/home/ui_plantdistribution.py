import json
import apps.home.dbquery as dbquery
import plotly
def getPlantDistribution(projeto_id):
    preferencias = dbquery.getDataframeResultset(f"select idFinalidade, idFormacao from ProjetoPreferencias pp "
                                            f"inner join MunicipioFito mf "
                                            f"on pp.idMunicipioFito = mf.id "
                                            f"inner join Fitofisionomia f "
                                            f"on mf.idFitoFisionomia = f.id "
                                            f"where idProjeto = {projeto_id} ")
    dict = dbquery.getListDictResultset(f"select descModelo as caption, ArquivoDesenho as fileName, id from ModeloPlantio "
                                       f"where idFinalidade = {preferencias.iloc[0].idFinalidade} "
                                       f"and  idFormacao = {preferencias.iloc[0].idFormacao} "
                                        f"order by descModelo")
    return json.dumps({'data': dict}, cls=plotly.utils.PlotlyJSONEncoder)

def savePlantDistribution(projeto_id, idModelo):
    dbquery.executeSQL(f"update ProjetoPreferencias "
                       f"set idModeloPlantio = {idModelo} where idProjeto = {projeto_id}")