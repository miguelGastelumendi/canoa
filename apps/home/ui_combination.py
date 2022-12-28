from apps.home import dbquery as dbquery

def getCombinations(idProjeto):
    df = dbquery.getDataframeResultset(
        f"select CONCAT('Escolha uma entre as opções para a faixa ',ft.nomeFaixa,'. Valores em R$/',cast(ft.AreaFaixa as decimal(10,2)),' m².') as nomeFaixa, "
        f"vfc.idFaixaTipo,  vfc.idCombinacao, vfc.Especies, vfc.TIR, vfc.payback, vfc.InvNecessario, VTLiquido, vfc.VPLiquido "
        f"from Projeto p "
        f"inner join MunicipioFito mf "
        f"on mf.id = p.idMunicipioFito "
        f"inner join Municipio m "
        f"on m.id = mf.idMunicipio "
        f"inner join (select distinct idModeloPlantio, idFaixaTipo from ModeloFaixa mf ) mf2 "
        f"on mf2.idModeloPlantio = p.idModeloPlantio "
        f"inner join v_filtraCombinacoes vfc on "
        f"vfc.idFaixaTipo = mf2.idFaixaTipo and "
        f"vfc.idFitofisionomia = mf.idFitoFisionomia and "
        f"vfc.idRegiaoEco = m.idRegiaoEco and "
        f"vfc.idRegiaoAdm = m.idRegiaoAdm and "
        f"vfc.idTopografia = p.idTopografia and "
        f"vfc.idMecanizacaoNivel = p.idMecanizacaoNivel "
        f"inner join FaixaTipo ft on ft.id =  mf2.idFaixaTipo "
        f"and p.id = {idProjeto} "
        f"order by idFaixaTipo,TIR DESC ")
    uniques = df.groupby(['nomeFaixa','idFaixaTipo'], as_index=False).count()
    return df, uniques[['nomeFaixa','idFaixaTipo']]