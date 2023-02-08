from apps.home import dbquery as dbquery

def getCombinations(idProjeto):
    df = dbquery.getDataframeResultset(
            f"select * from v_EscolhaCombinacaoPorFaixa "
            f"where idProjeto = {idProjeto} "
            f"order by idFaixaTipo, TIR DESC")
    uniques = df.groupby(['nomeFaixa','idFaixaTipo'], as_index=False).count()
    return df, uniques[['nomeFaixa','idFaixaTipo']], len(df) == 0
