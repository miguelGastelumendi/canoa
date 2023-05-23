from apps.home import dbquery as dbquery

def getCombinations(idProjeto):
    df = dbquery.getDataframeResultset(f"""
select ecp.*,case 
		       when pcf.idFluxoCaixa is not null then 1
		       else 0
		     end as selected from v_EscolhaCombinacaoPorFaixa ecp
left join ProjetoCombFaixa pcf
on ecp.idFluxoCaixa = pcf.idFluxoCaixa 
where ecp.idProjeto = {idProjeto}
order by ecp.idFaixaTipo, ecp.TIR DESC""")
    uniques = df.groupby(['nomeFaixa','idFaixaTipo'], as_index=False).count()
    return df, uniques[['nomeFaixa','idFaixaTipo']], len(df) == 0
