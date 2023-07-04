import json
import apps.home.dbquery as dbquery
import plotly
def getPlantDistribution(projeto_id):
    dict = dbquery.getListDictResultset(
	"select mp.descModelo as caption,"
	"mp.ArquivoDesenho as fileName,"
	"mp.id,"
	"case "
		"when p.idModeloPlantio = mp.id then 1 "
		"else 0 "
	"end as selected "
    "from "
	"Projeto p "
    "inner join MunicipioFito mf "
    "on p.idMunicipioFito = mf.id "
    "inner join Fitofisionomia f on "
	"mf.idFitoFisionomia = f.id "
    "inner join ModeloPlantio mp " 
    "on mp.idFinalidade = p.idFinalidade "  
    "and mp.idFormacao = f.idFormacao "
    f"where p.id = {projeto_id}")
    return dict

def savePlantDistribution(projeto_id, idModelo):
    dbquery.executeSQL(f"update Projeto "
                       f"set idModeloPlantio = {idModelo} where id = {projeto_id}")