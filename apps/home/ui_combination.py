from apps.home import dbquery as dbquery

def getCombinations(idProjeto):
    df = dbquery.getDataframeResultset(
        f"select CONCAT('Escolha uma entre as opções para a faixa ',ft.nomeFaixa,'. Valores em R$/',cast(ft.AreaFaixa as decimal(10,2)),' m².') as nomeFaixa, "
        f"vfc.idFaixaTipo,  vfc.idCombinacao, vfc.Especies, vfc.TIR, vfc.payback, vfc.InvNecessario, VTLiquido, vfc.VPLiquido "
        f"from ProjetoPreferencias pp "
        f"inner join MunicipioFito mf "
        f"on mf.id = pp.idMunicipioFito "
        f"inner join Municipio m "
        f"on m.id = mf.idMunicipio "
        f"inner join (select distinct idModeloPlantio, idFaixaTipo from ModeloFaixa mf ) mf2 "
        f"on mf2.idModeloPlantio = pp.idModeloPlantio "
        f"inner join v_filtraCombinacoes vfc on "
        f"vfc.idFaixaTipo = mf2.idFaixaTipo and "
        f"vfc.idFitofisionomia = mf.idFitoFisionomia and "
        f"vfc.idRegiaoEco = m.idRegiaoEco and "
        f"vfc.idRegiaoAdm = m.idRegiaoAdm and "
        f"vfc.idTopografia = pp.idTopografia and "
        f"vfc.idMecanizacaoNivel = pp.idMecanizacaoNivel "
        f"inner join FaixaTipo ft on ft.id =  mf2.idFaixaTipo "
        f"and pp.idProjeto = {idProjeto} "
        f"order by idFaixaTipo,TIR DESC ")
    return df, df.nomeFaixa.unique().tolist()