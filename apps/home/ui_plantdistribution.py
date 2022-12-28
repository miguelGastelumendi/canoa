import json
import apps.home.dbquery as dbquery
import plotly
def getPlantDistribution(projeto_id):
    projeto = dbquery.getDataframeResultset(f"select idFinalidade, idFormacao from Projeto p "
                                            f"inner join MunicipioFito mf "
                                            f"on p.idMunicipioFito = mf.id "
                                            f"inner join Fitofisionomia f "
                                            f"on mf.idFitoFisionomia = f.id "
                                            f"where p.id = {projeto_id} ")
    dict = dbquery.getListDictResultset(f"select descModelo as caption, ArquivoDesenho as fileName, id from ModeloPlantio "
                                       f"where idFinalidade = {projeto.iloc[0].idFinalidade} "
                                       f"and  idFormacao = {projeto.iloc[0].idFormacao} "
                                        f"order by descModelo")
    return json.dumps({'data': dict}, cls=plotly.utils.PlotlyJSONEncoder)

def savePlantDistribution(projeto_id, idModelo):
    dbquery.executeSQL(f"update Projeto "
                       f"set idModeloPlantio = {idModelo} where id = {projeto_id}")