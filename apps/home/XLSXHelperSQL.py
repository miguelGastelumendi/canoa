SQLs = {
    'userNameDescProjeto': """select u.username, descProjeto, p.eMailEnvioResultado 
from Projeto p 
inner join Users u 
on p.idUser = u.id 
where p.id = {0}""",

    'Identificação': """select us.username,
       pj.descProjeto, fn.desFinalidade,
       mu.nomeMunicipio,  ff.descFitofisionomia,
       re.nomeRegiaoEco, ra.nomeRegiaoAdm, tp.nomeTopografia,
       mn.nomeMecanizacao 
  from Projeto pj
       inner join Users us          on us.id = pj.idUser 
       inner join Finalidade fn     on fn.id = pj.idFinalidade  
       inner join MunicipioFito mf  on mf.id = pj.idMunicipioFito 
       inner join Municipio mu      on mu.id = mf.idMunicipio 
       inner join FitoFisionomia ff on ff.id = mf.idFitoFisionomia 
       inner join RegiaoEco re      on re.id = mu.idRegiaoEco 
       inner join RegiaoAdm ra      on ra.id = mu.idRegiaoAdm 
       inner join Topografia tp     on tp.id = pj.idTopografia 
       inner join MecanizacaoNivel mn on mn.id = pj.idMecanizacaoNivel 
       where pj.id = {0}
 """,

    'Silvicultura': """select ps.idCombinacao, 
       ft.nomeFaixa Faixa, ff.descFitofisionomia FitoFisionomia , re.nomeRegiaoEco RegiaoEco, 
       ra.nomeRegiaoAdm RegiaoAdm, t.nomeTopografia Topografia, mn.nomeMecanizacao Mecanizacao, 
       es.nomeComum Especie, ps.areaOcupacao, ps.numArvores, pd.nomeProduto Produto, 
       cl.nomeClasse Classe, et.nomeEtapa Etapa, ps.Ano, 
       op.nomeOperacao Operacao, rc.nomeRecurso Recurso, ps.qtdRecurso, ps.siglaUnidade, ps.Preco 
  from ProjetoSilvicultura ps 
       inner join FaixaTipo ft        on ft.id = ps.idFaixaTipo 
       inner join FitoFisionomia ff   on ff.id = ps.idFitoFisionomia 
       inner join RegiaoEco re        on re.id = ps.idRegiaoEco 
       inner join RegiaoAdm ra        on ra.id = ps.idRegiaoAdm 
       inner join Topografia t        on t.id  = ps.idTopografia 
       inner join MecanizacaoNivel mn on mn.id = ps.idMecanizacaoNivel 
       inner join Especie es          on es.id  = ps.idespecie 
       inner join Produto pd          on pd.id  = ps.idProduto 
       inner join CustoClasse cl      on cl.id  = ps.idClasse 
       inner join CustoEtapa et       on et.id  = ps.idCustoEtapa 
       inner join Operacao op         on op.id  = ps.idOperacao 
       inner join Recurso rc          on rc.id  = ps.idRecurso 
where ps.idProjeto = {0} 
order by ps.idCombinacao, es.nomeComum, pd.nomeProduto, 
      cl.nomeClasse, et.nomeEtapa, ps.Ano, 
      op.nomeOperacao, rc.nomeRecurso
""",

    'Receitas': """select pr.idCombinacao, ft.nomeFaixa Faixa,
       ff.descFitofisionomia FitoFisionomia , re.nomeRegiaoEco RegiaoEco, 
       ra.nomeRegiaoAdm RegiaoAdm, 
       e.nomeComum Especie, pr.areaOcupacao, pr.numArvores, 
       p.nomeProduto Produto,
       pr.Idade, i.descIntervencao, pr.ProdPlanta,  pr.Preco
  from ProjetoReceita pr
       inner join FaixaTipo ft      on ft.id = pr.idFaixaTipo 
       inner join FitoFisionomia ff on ff.id = pr.idFitoFisionomia 
       inner join RegiaoEco re      on re.id = pr.idRegiaoEco 
       inner join RegiaoAdm ra      on ra.id = pr.idRegiaoAdm 
       inner join Especie e         on e.id  = pr.idEspecie 
       inner join Produto p         on p.id  = pr.idProduto 
       inner join Intervencao i     on i.id  = pr.idIntervencao  
 where pr.idProjeto = {0}
order by pr.idCombinacao, e.nomeComum, p.nomeProduto, pr.Idade""",

    'Unidades': """select distinct rc.nomeRecurso Recurso, ps.siglaUnidade Unidade
  from ProjetoSilvicultura ps 
       inner join Recurso rc          on rc.id  = ps.idRecurso 
where ps.idProjeto = {0} 
order by rc.nomeRecurso, ps.siglaUnidade""",

    'Faixas': """select ft.nomeFaixa Faixa, mf.qtdModeloFaixa QtdFaixas, ft.AreaFaixa
  from Projeto pj
       inner join V_ModeloFaixa mf on mf.idModeloPlantio = pj.idModeloPlantio 
       inner join FaixaTipo ft on ft.id = mf.idFaixaTipo 
 where pj.id = {0}""",
    
    'txDsc': f"""select valorParametro TxDsc 
  from Parametro p 
 where p.nomeParametro = 'TxDsc'""",

    'ResumoSilvicultura': """select * 
from ( 
      select distinct 
             ps.idCombinacao, 
             ft.nomeFaixa Faixa, ff.descFitofisionomia FitoFisionomia , re.nomeRegiaoEco RegiaoEco, 
             ra.nomeRegiaoAdm RegiaoAdm, t.nomeTopografia Topografia, mn.nomeMecanizacao Mecanizacao, ps.Ano,
             op.nomeOperacao Operacao, rc.nomeRecurso Recurso
        from ProjetoSilvicultura ps 
             inner join FaixaTipo ft        on ft.id = ps.idFaixaTipo 
             inner join FitoFisionomia ff   on ff.id = ps.idFitoFisionomia 
             inner join RegiaoEco re        on re.id = ps.idRegiaoEco 
             inner join RegiaoAdm ra        on ra.id = ps.idRegiaoAdm 
             inner join Topografia t        on t.id  = ps.idTopografia 
             inner join MecanizacaoNivel mn on mn.id = ps.idMecanizacaoNivel 
             inner join Operacao op         on op.id  = ps.idOperacao 
             inner join Recurso rc          on rc.id  = ps.idRecurso 
       where ps.idProjeto = {0} 
      ) x
order by 1,2,3,4,5,6,7,8,9,10""",
    
    'FluxoCaixaFaixa': """select * 
  from (
        select distinct 
               ps.idCombinacao, 
               ft.nomeFaixa Faixa, ps.Ano
          from ProjetoSilvicultura ps 
               inner join FaixaTipo ft on ft.id = ps.idFaixaTipo 
         where ps.idProjeto = {0} 
        ) x
  order by 1,2,3 """,

    'Distribuição': """select * from ProjetoDistribuicao pd 
where pd.idProjeto = {0}
""",

    'tbDistribuicao': """select ge.nomeFaixa Faixa, gr.NomeGrupo Grupo, ge.nomeComum Especie, ge.nomeCientifico,
       sum(ge.numArvores)*m.qtdModeloFaixa numArvores
  from (select r.idFaixaTipo, f.NomeFaixa, e.nomeComum, e.nomeCientifico, max(r.numArvores) NumArvores,
              min(case when e.FlagBordadura = 'T' then 1
                       when ((e.FlagBordadura is null) or (e.FlagBordadura <> 'T')) and  
                             p.flagMadeireiro = 'T' and f.ProibeMadeireira = 'F' then 2 
                      else 3
                  end) idGrupo     
         from ProjetoReceita r
              inner join Especie e       on e.id = r.idEspecie  
              inner join Produto p       on p.id = r.idProduto 
              inner join FaixaTipo f     on f.id = r.idFaixaTipo 
        where r.idProjeto = {0}       
        group by r.idFaixaTipo, f.NomeFaixa, f.Largura, e.nomeComum, e.nomeCientifico
       ) ge 
       inner join V_ModeloFaixa m on m.idModeloPlantio = (select idModeloPlantio from Projeto where id = {0}) and  
                                     m.idFaixaTipo     = ge.idFaixaTipo
       inner join EspGrpDistribuicao gr on gr.id = ge.idGrupo
 group by ge.nomeFaixa, gr.NomeGrupo, ge.nomeComum, ge.nomeCientifico, m.qtdModeloFaixa""",

    'faixasDistribuicao': """select mf.*,ft.* from Projeto p
inner join ModeloPlantio mp 
on p.idModeloPlantio = mp.id 
inner join ModeloFaixa mf 
on mf.idModeloPlantio = mp.id
inner join FaixaTipo ft 
on mf.idFaixaTipo = ft.id
where p.id = 314
order by mf.OrdemFaixa 
 """,
    'TxPoup': """select valorParametro as TxPoup from Parametro
where nomeParametro = 'TxPoup'""",
    'sendEMailData': "select eMailEnvioResultado, descProjeto "
                     "from Projeto p where id = {0}"
}