import apps.home.dbquery as dbquery

def updateProjectData(project_id: str, selectedCombinations: str):
    return dbquery.getDictResultset(f"select CONCAT('Escolha uma entre as opções para a faixa ',ft.nomeFaixa,'. Valores em R$/',cast(ft.AreaFaixa as decimal(10,2)),' m².') as nomeFaixa, "
            f"vfc.idFaixaTipo,  vfc.idCombinacao, vfc.Especies, vfc.TIR, vfc.payback, vfc.InvNecessario, VTLiquido, vfc.VPLiquido "
            f"from Projeto p "
            f"inner join MunicipioFito mf on mf.id = p.idMunicipioFito "
            f"inner join Municipio m on m.id = mf.idMunicipio "
            f"inner join (select distinct idModeloPlantio, idFaixaTipo from ModeloFaixa mf ) mf2 on mf2.idModeloPlantio = p.idModeloPlantio "
            f"inner join v_filtraCombinacoes vfc on vfc.idFaixaTipo = mf2.idFaixaTipo and vfc.idFitofisionomia = mf.idFitoFisionomia "
                   f"and vfc.idRegiaoEco = m.idRegiaoEco and vfc.idRegiaoAdm = m.idRegiaoAdm and vfc.idTopografia = p.idTopografia and vfc.idMecanizacaoNivel = p.idMecanizacaoNivel "
            f"inner join FaixaTipo ft on ft.id =  mf2.idFaixaTipo " 
            f"where p.id = {project_id} "
            f"and vfc.idCombinacao in (12809,13023) "
            f"order by idFaixaTipo,TIR DESC")

def getProjectData(project_id: str, selectedCombinations: str):
    return dbquery.getDictResultset(f"select CONCAT('Escolha uma entre as opções para a faixa ',ft.nomeFaixa,'. Valores em R$/',cast(ft.AreaFaixa as decimal(10,2)),' m².') as nomeFaixa, "
            f"vfc.idFaixaTipo,  vfc.idCombinacao, vfc.Especies, vfc.TIR, vfc.payback, vfc.InvNecessario, VTLiquido, vfc.VPLiquido "
            f"from Projeto p "
            f"inner join MunicipioFito mf on mf.id = p.idMunicipioFito "
            f"inner join Municipio m on m.id = mf.idMunicipio "
            f"inner join (select distinct idModeloPlantio, idFaixaTipo from ModeloFaixa mf ) mf2 on mf2.idModeloPlantio = p.idModeloPlantio "
            f"inner join v_filtraCombinacoes vfc on vfc.idFaixaTipo = mf2.idFaixaTipo and vfc.idFitofisionomia = mf.idFitoFisionomia "
                   f"and vfc.idRegiaoEco = m.idRegiaoEco and vfc.idRegiaoAdm = m.idRegiaoAdm and vfc.idTopografia = p.idTopografia and vfc.idMecanizacaoNivel = p.idMecanizacaoNivel "
            f"inner join FaixaTipo ft on ft.id =  mf2.idFaixaTipo " 
            f"where p.id = {project_id} "
            f"and vfc.idCombinacao in ({selectedCombinations.replace('-',',')}) "
            f"order by idFaixaTipo,TIR DESC")

