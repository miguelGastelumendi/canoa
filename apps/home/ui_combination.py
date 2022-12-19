from apps.home import dbquery as dbquery

def getCombinations(idProjeto):
    df = dbquery.getDataframeResultset(
        f"select ft.nomeFaixa,  vfc.idFaixaTipo,  vfc.idCombinacao, vfc.Especies, vfc.TIR, vfc.payback, vfc.InvNecessario, VTLiquido, vfc.VPLiquido "
        f"from v_filtraCombinacoes vfc "
        f"inner join FaixaTipo ft "
        f"on vfc.idFaixaTipo = ft.id "
        f"inner join ProjetoPreferencias pp "
        f"on pp.idTopografia = vfc.idTopografia "
        f"and pp.idMecanizacaoNivel = vfc.idMecanizacaoNivel "
        f"inner join MunicipioFito mf "
        f"on pp.idMunicipioFito = mf.id "
        f"and vfc.idFitofisionomia = mf.idFitoFisionomia "
        f"inner join Municipio m "
        f"on mf.idMunicipio = m.id "
        f"and vfc.idRegiaoEco = m.idRegiaoEco "
        f"and vfc.idRegiaoAdm = m.idRegiaoAdm "
        f"where vfc.idFaixaTipo in (select idFaixaTipo from ModeloFaixa mf2 where idModeloPlantio = pp.idModeloPlantio) " 
        f"and vfc.TIR > 0 "
        f"and pp.idProjeto = {idProjeto} "
        f"order by idFaixaTipo,TIR DESC ")
    return df, df.nomeFaixa.unique().tolist()