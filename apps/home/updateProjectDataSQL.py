sqls = {
        "deleteProjetoSilvicultura": "delete from  ProjetoSilvicultura where idProjeto = @idProjeto",
        "insertProjetoSilvicultura": """        
	 insert into ProjetoSilvicultura 
	(idProjeto, idFluxoCaixa,
	 idFaixaTipo, idFitoFisionomia, idRegiaoEco, 
	 idCombinacao, idRegiaoAdm, idTopografia, idMecanizacaoNivel, 
	 idespecie, idProduto, numArvores, areaOcupacao, 
	 Ano, 
	 idClasse, idCustoEtapa, idOperacao, idRecurso, 
	 qtdRecurso, siglaUnidade, Preco, qtdRecEspFaixa, ValorEspFaixa )
	select cf.idProjeto,
	       cf.idFluxoCaixa,
	       vtc.idFaixaTipo, vtc.idFitoFisionomia, vtc.idRegiaoEco, 
	       vtc.idCombinacao, vtc.idRegiaoAdm, vtc.idTopografia, vtc.idMecanizacaoNivel, 
	       vtc.idespecie, vtc.idProduto, vtc.numArvores, vtc.areaOcupacao, 
	       vtc.Ano, 
	       vtc.idClasse, vtc.idCustoEtapa, vtc.idOperacao, vtc.idRecurso, 
	       vtc.qtdRecurso, vtc.siglaUnidade, vtc.Preco, vtc.qtdRecEspFaixa, vtc.ValorEspFaixa 
	  from VT_CombinaFcCustos vtc
	       inner join 
	             (select pcf.idProjeto, 
	                     pcf.idFluxoCaixa, 
	                     pcf.idCombinacao, m.idRegiaoAdm, prj.idTopografia, prj.idMecanizacaoNivel 
	                from Projeto prj 
	                     inner join MunicipioFito mf on mf.id = prj.idMunicipioFito 
	                     inner join Municipio m on m.id = mf.idMunicipio 
	                     inner join ProjetoCombFaixa pcf on pcf.idProjeto = prj.id
	               where prj.id = @idProjeto
	              ) cf  
	        on cf.idCombinacao = vtc.idCombinacao and 
	           cf.idRegiaoAdm  = vtc.idRegiaoAdm  and
	           cf.idTopografia = vtc.idTopografia and  
	           cf.idMecanizacaoNivel = vtc.idMecanizacaoNivel""",

        "deleteProjetoReceita": "delete from  ProjetoReceita where idProjeto = @idProjeto",
        "insertProjetoReceita": """
	Insert into ProjetoReceita
	       (idProjeto, idFluxoCaixa,
	        idFaixaTipo, idFitoFisionomia, idRegiaoEco, idCombinacao, idRegiaoAdm,  
	        idespecie, areaOcupacao, idProduto, Idade, idIntervencao, 
	        ProdPlanta, numArvores, Preco, ProdFaixa, ValorEspFaixa)
	 select cf.idProjeto,
	        cf.idFluxoCaixa,
	        vtr.idFaixaTipo, vtr.idFitoFisionomia, vtr.idRegiaoEco, vtr.idCombinacao, vtr.idRegiaoAdm,  
	        vtr.idespecie, vtr.areaOcupacao, vtr.idProduto, vtr.Idade, vtr.idIntervencao, 
	        vtr.ProdPlanta, vtr.numArvores, vtr.Preco, vtr.ProdFaixa, vtr.ValorEspFaixa
	   from VT_CombinaFcReceitas vtr
	        inner join 
	             (select pcf.idProjeto, 
	                     pcf.idFluxoCaixa, 
	                     pcf.idCombinacao, m.idRegiaoAdm 
	                from Projeto prj 
	                     inner join MunicipioFito mf on mf.id = prj.idMunicipioFito 
	                     inner join Municipio m on m.id = mf.idMunicipio 
	                     inner join ProjetoCombFaixa pcf on pcf.idProjeto = prj.id
	               where prj.id = @idProjeto
	              ) cf  
	        on cf.idCombinacao  = vtr.idCombinacao and 
	           cf.idRegiaoAdm   = vtr.idRegiaoAdm""",

	    "deleteProjetoFcModelo" : "delete from ProjetoFcModelo where idProjeto = @idProjeto",
	    "InsertProjetoFcModelo": """
	     Insert into ProjetoFcModelo
	       (idProjeto, ano, 
	        VTReceitas, VTCustos, VTLiquido,
	        VPReceitas, VPCustos, VPLiquido,
	        VALiquido)
	select somaFC.idProjeto, somaFC.ano,
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
	                       on prj.id = @idProjeto
	               inner join V_ModeloFaixa mf 
	                       on mf.idModeloPlantio = prj.idModeloPlantio and 
	                          mf.idFaixaTipo = fcr.idFaixaTipo
	               inner join ProjetoCombFaixa pcf 
	                       on pcf.idProjeto = prj.id and   
	                          pcf.idFaixaTipo = mf.idFaixatipo and   
	                          pcf.idFluxoCaixa = fcr.idFluxoCaixa 
	
	      ) somaFC
	 group by somaFC.idProjeto, somaFC.ano
	 order by somaFC.idProjeto, somaFC.ano""",

       "updateProjeto": """
update prj 
set prj.VTReceitas    = ind.VTReceitas, 
    prj.VTCustos      = ind.VTCustos,
    prj.VTLiquido     = ind.VTLiquido,
    prj.VPReceitas    = ind.VPReceitas,
    prj.VPCustos      = ind.VPCustos,
    prj.VPLiquido     = ind.VPLiquido,
    prj.payBack       = ind.payBack,
    prj.InvNecessario = ind.InvNecessario,
    prj.TIR = ind.TIR
from Projeto prj 
inner join
    (select sm.idProjeto, 
            sm.VTReceitas, sm.VTCustos, sm.VTLiquido,
            sm.VPReceitas, sm.VPCustos, sm.VPLiquido,
            pb.payBack, iv.InvNecessario, tr.TIR
      from (select idProjeto, 
                   sum(VTReceitas) VTReceitas, sum(VTCustos) VTCustos, sum(VTLiquido) VTLiquido,
                   sum(VPReceitas) VPReceitas, sum(VPCustos) VPCustos, sum(VPLiquido) VPLiquido
              from ProjetoFcModelo
             group by idProjeto ) sm
       inner join
            (select fc1.idProjeto, min(fc1.ano) payBack 
               from ProjetoFcModelo fc1
              where fc1.VALiquido > 0
              group by fc1.idProjeto) pb
       on pb.idProjeto = sm.idProjeto
       inner join
            (select fc2.idProjeto, -1.00*min(fc2.VALiquido) InvNecessario
               from ProjetoFcModelo fc2
              group by fc2.idProjeto) iv   
       on iv.idProjeto = sm.idProjeto   
       inner join 
             (select fc3.idProjeto,
                     round([dbo].[fn_IRR](string_agg(round(fc3.VTLiquido,2),',') WITHIN GROUP (ORDER BY fc3.ano) , 0.0000000001,rand()),5) as TIR
                from ProjetoFcModelo fc3
               group by fc3.idProjeto) tr
        on tr.idProjeto = sm.idProjeto
       ) ind
on ind.idProjeto = prj.id
where prj.id = @idProjeto"""}
