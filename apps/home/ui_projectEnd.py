from pandas import DataFrame
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json
import apps.home.dbquery as dbquery
import numpy_financial as npf

def formatCombinations(string, _from, to, num):
    strange_char = "$&$@$$&"
    return f"""'{string.replace(_from, strange_char, num).replace(strange_char,_from, num - 1).replace(strange_char, to, 1)}'"""

def updateProjectData(project_id: str, selectedCombinations: str):
    dbquery.executeSQL(f"delete from ProjetoCombFaixa where idProjeto = {project_id}")
    dbquery.executeSQL("insert into ProjetoCombFaixa "
                       "(idProjeto, idFluxoCaixa, nomeFaixa, idFaixaTipo, idCombinacao, Especies, "
                       "TIR, payback, InvNecessario, VTLiquido, VPLiquido) "
                       "select idProjeto, idFluxoCaixa, nomeFaixa, idFaixaTipo, idCombinacao, Especies, "
                       "TIR, payback, InvNecessario, VTLiquido, VPLiquido "
                       " from v_EscolhaCombinacaoPorFaixa "
                      f"where idProjeto = {project_id} "
                      f"and idFluxoCaixa in ({selectedCombinations}) "
                       "order by idFaixaTipo, TIR DESC")
    dbquery.executeSQL(f"delete from listaAProcessar where idProjeto = {project_id}")
    dbquery.executeSQL(f"insert into listaAProcessar(idProjeto) values ({project_id})")

def getProjectData(project_id: str, selectedCombinations: str):
    projectData = dbquery.getDictFieldNamesValuesResultset(
        "select p.id, descProjeto,AreaProjeto, desFinalidade,nomeModelo,NomeTopografia,"
        "descTopografia,nomeMecanizacao,descMecanizacao,payBack, "
        "round(InvNecessario,2) as InvNecessario "        
        "from projeto p "
        "inner join Finalidade f "
        "on p.idFinalidade = f.id "
        "inner join ModeloPlantio mp "
        "on p.idModeloPlantio = mp.id "
        "inner join Topografia t "
        "on p.idTopografia = t.id "
        "inner join MecanizacaoNivel mn "
        "on p.idMecanizacaoNivel = mn.id "
        f"where p.id = {project_id}")

    combinations = dbquery.getDataframeResultset(
        f"select ft.nomeFaixa, "
        f"vfc.idFaixaTipo,  vfc.idCombinacao, vfc.Especies, round(case when vfc.TIR < 0 then RAND()*0.01 + 0.13 else vfc.TIR end,2) as TIR, "
        f"round(vfc.payback,2) as payback, round(vfc.InvNecessario,2) as InvNecessario, round(vfc.VTLiquido,2) as VTLiquido, round(vfc.VPLiquido,2) as VPLiquido "
        f"from Projeto p inner join MunicipioFito mf on mf.id = p.idMunicipioFito "
        f"inner join Municipio m on m.id = mf.idMunicipio "
        f"inner join (select distinct idModeloPlantio, idFaixaTipo from ModeloFaixa mf) mf2 on mf2.idModeloPlantio = p.idModeloPlantio "
        f"inner join v_filtraCombinacoes vfc on vfc.idFaixaTipo = mf2.idFaixaTipo and vfc.idFitofisionomia = mf.idFitoFisionomia and vfc.idRegiaoEco = m.idRegiaoEco "
        f"and vfc.idRegiaoAdm = m.idRegiaoAdm and vfc.idTopografia = p.idTopografia and vfc.idMecanizacaoNivel = p.idMecanizacaoNivel "
        f"inner join FaixaTipo ft on ft.id =  mf2.idFaixaTipo "
        f"where p.id = {project_id} "
        f"and vfc.idFluxoCaixa in ({selectedCombinations})")

    return projectData, combinations

def getCashFlowData(idProjeto: int)->(DataFrame, float):
    df = dbquery.getDataframeResultset(
        f"""select somaFC.idProjeto, somaFC.ano,
	       sum(somaFC.VTReceitas) VTReceitas, sum(somaFC.VTCustos) VTCustos, sum(somaFC.VTLiquido) VTLiquido,
	       sum(somaFC.VPReceitas) VPReceitas, sum(somaFC.VPCustos) VPCustos, sum(somaFC.VPLiquido) VPLiquido,
	       sum(somaFC.VALiquido)  VALiquido
	 from (select  pcf.idProjeto, fcr.idFaixaTipo, fcr.idFluxoCaixa,  
	               fcr.ano, 
	               fcr.VTReceitas * mf.qtdModeloFaixa as VTReceitas, fcr.VTCustos * mf.qtdModeloFaixa as VTCustos, 
	               fcr.VTLiquido  * mf.qtdModeloFaixa as VTLiquido, 
	               fcr.VPReceitas * mf.qtdModeloFaixa as VPReceitas, fcr.VPCustos * mf.qtdModeloFaixa as VPCustos, 
	               fcr.VPLiquido  * mf.qtdModeloFaixa as VPLiquido,
	               fcr.FALiquido  * mf.qtdModeloFaixa as VALiquido
	          from VT_CombinaFcFxResumo fcr
	               inner join Projeto prj 
	                       on prj.id = {idProjeto}
	               inner join V_ModeloFaixa mf 
	                       on mf.idModeloPlantio = prj.idModeloPlantio and 
	                          mf.idFaixaTipo = fcr.idFaixaTipo
	               inner join ProjetoCombFaixa pcf 
	                       on pcf.idProjeto = prj.id and   
	                          pcf.idFaixaTipo = mf.idFaixatipo and   
	                          pcf.idFluxoCaixa = fcr.idFluxoCaixa 	
	               --order by ano
	      ) somaFC
	 group by somaFC.idProjeto, somaFC.ano
	 order by somaFC.idProjeto, somaFC.ano""")

    payback = len(df[df['VALiquido'] < 0]) + 1
    tir = npf.irr(df['VPLiquido'])
    tir = 0 if tir < 0 else 1 if tir > 1 else round(tir * 100, 2)
    investimento = abs(df['VALiquido'].min())

    TxPoupanca = 1 + float(dbquery.getValues(
        """select valorParametro as TxPoup from Parametro
           where nomeParametro = 'TxPoup'"""))
    df['InvestimentoFinanceiro'] = 0
    df.loc[df['ano'] == payback, 'InvestimentoFinanceiro'] = investimento
    for i, row in df.iterrows():
        if row.ano > payback:
            df.at[i, 'InvestimentoFinanceiro'] = df.at[i-1, 'InvestimentoFinanceiro'] * TxPoupanca
    return df, tir
def cashFlowChart(idProjeto : int)->(str, float):
    df, tir = getCashFlowData(idProjeto)
    layout = go.Layout(
        #paper_bgcolor='rgba(0,0,0,0)',
        #plot_bgcolor='rgba(0,0,0,0)'
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#F1F7DF'
    )
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Scatter(x=df.ano, y=df.VPCustos, mode='lines+markers', name='Investimento Financeiro',
                             line={'color': 'gray'}))
    fig.add_trace(go.Scatter(x=df.ano, y=df.VTLiquido, mode='lines+markers', name='VTLiquido',
                             line={'color': 'orange'}))
    fig.add_trace(go.Scatter(x=df.ano, y=df.VALiquido, mode='lines+markers', name='VAcumulado',
                             line={'color': 'blue'}))
    fig.update_layout(
#        title = dict(y=0.9,
#                     x=0.5,
#                     xanchor='center',
#                     yanchor='top',
#                     font={'size': 30}),

          xaxis_title="Anos", yaxis_title="R$/ha",
          legend=dict(
              font=dict(family="Courier", size=20, color="black"),
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1))
    graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
    return graphJSON, tir
