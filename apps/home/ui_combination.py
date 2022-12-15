from apps.home import dbquery as dbquery

def getCombinations(idProjeto):
    df = dbquery.getDataframeResultset(
        f"select ft.nomeFaixa,  vfc.idFaixaTipo,  "
        f"vfc.idCombinacao, vfc.Especies, "
        f"vfc.TIR, vfc.payback, vfc.InvNecessario, VTLiquido, vfc.VPLiquido "
        f"from v_filtraCombinacoes vfc "
        f"inner join FaixaTipo ft "
        f"on vfc.idFaixaTipo = ft.id "
        f"where vfc.idFaixaTipo in (1,2) "
        f"and vfc.idFitofisionomia = 10 "
        f"and vfc.idRegiaoEco = 3 "
        f"and vfc.idRegiaoAdm = 5 "
        f"and vfc.idTopografia = 3 "
        f"and vfc.idMecanizacaoNivel = 1 "
        f"and vfc.TIR > 0 "
        f"order by nomeFaixa,TIR DESC ")
    return df, df.nomeFaixa.unique().tolist()