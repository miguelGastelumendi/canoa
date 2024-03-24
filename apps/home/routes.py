# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
#mgd from flask import render_template, request, Markup
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
import apps.home.ui_projectSupport as ui_projectSupport
import apps.home.ui_plantdistribution as ui_plantdistribution
import apps.home.dbquery as dbquery
import apps.home.ui_combination as ui_combination
import apps.home.ui_projectEnd as ui_projectEnd
from flask import session
from apps.home import helper
from flask_login import current_user
import re
import json
import apps.home.logHelper as logHelper

log = logHelper.Log2Database()

# ============= Index ============== #
@blueprint.route('/index')
# @login_required não pode ter, index é 'livre', depende do menu
def index():
    return render_template('home/index.html', pageTitle='Home')


# ============= Documents ============== #
@blueprint.route('/docs/<docName>')
def docs(docName):
    return render_template('layouts/documentDisplay.html',  **{'documentTitle': f'{docName} Document', 'pageTitle':f'{docName}'})


# ======== Route Callback ========== #
@blueprint.route('/callback/<endpoint>')
@login_required
def route_callback(endpoint):
    log.logActivity2Database(
          idUsuario= current_user.id if current_user else 'NULL'
        , idProjeto= 'NULL' if not '_projeto_id' in session.keys() else session['_projeto_id']
        , url=f"{endpoint}\{str(request.args.to_dict(flat=True))}"
    )

    args = request.args
    callerID = args.get('callerID')

    if callerID == 'mapSP':
        return ui_projectSupport.getMapSP()

    elif endpoint == 'projectName':
        try:
            if not '_projeto_id' in session.keys() or session['_projeto_id'] == -1:
                session['_projeto_id'] = ui_projectSupport.createProject(current_user.id, request.args['projectName'])
            else:
                ui_projectSupport.updateProject(session['_projeto_id'], descProjeto=request.args['projectName'])
        except Exception as e:
            if '23000' in re.split('\W+', e.args[0]):
                return helper.getErrorMessage('projectNameMustBeUnique')
        return "Ok"

    elif endpoint == 'areas':
        try:
            ui_projectSupport.updateProject(session['_projeto_id'], **{'areaPropriedade': args['propertyArea'],
                                                                       'areaProjeto': args['projectArea']})
        except Exception as e:
            if '23000' in re.split('\W+', e.args[0]):
                return helper.getErrorMessage('projectNameMustBeUnique')
        return "Ok"

    elif endpoint == 'locationCAR':
        return ui_projectSupport.getMapCAR(request.args.get('CAR'))
    elif endpoint == 'locationLatLon':
        _, municipioFito = ui_projectSupport.getMunicipioFitoByLatLon(request.args['lat'], request.args['lon'])
        ui_projectSupport.updateProject(session['_projeto_id'], **{'idMunicipioFito': municipioFito.id[0], 'Lat': request.args['lat'],
                                                                   'Lon': request.args['lon']})
        return ui_projectSupport.getMapLatLon(request.args['lat'], request.args['lon'])
    elif endpoint == 'areas':
        if args.get('propertyArea') == '' or args.get('projectArea') == '':
            return helper.getErrorMessage('areasMustBeInformed')
        dbquery.executeSQL(f"UPDATE projeto SET AreaProjeto = {args.get('projectArea')}, "
                           f"AreaPropriedade = {args.get('propertyArea')} "
                           f"where id = {session['_projeto_id']}")

    elif endpoint == 'updateFormData':
        try:
            idMunicipio = int(args.get('idMunicipio'))
        except:
            idMunicipio = -1
        try:
            idFito = int(args.get('idFito'))
        except:
            idFito = -1
        if idFito > -1:
            ui_projectSupport.updateProject(session['_projeto_id'],
                                            **{'idMunicipioFito': idFito})
        return ui_projectSupport.getMapFitoMunicipio(idMunicipio,
                                                     idFito)
    elif endpoint == 'sendProjectEMail':
        to = request.args['user_email']
        dbquery.executeSQL(f"UPDATE Projeto set eMailEnvioResultado = '{to}' "
                           f"where id = {session['_projeto_id']}")
        ui_projectEnd.updateListaAProcessar(session['_projeto_id'])
    elif endpoint == 'help':
        return helper.getTipText(args.get('id'))
    return "Ok"

# =========== template ============= #
@blueprint.route('/<template>')
@login_required
def route_template(template):
    log.logActivity2Database(idUsuario=current_user.id if current_user else 'NULL',
    idProjeto='NULL' if not '_projeto_id' in session.keys() or session['_projeto_id'] == -1 else session['_projeto_id'], url=
                             f"{template}\{str(request.args.to_dict(flat=True))}")
    projectId = -1
    try:
        if template.find('.html') > -1:
            page2Send = helper.get_segment(request)
            if page2Send == 'rsp-projectStart.html':
                session['_projeto_id'] = -1
                return render_template("home/" + template,
                                       **helper.getFormText('rsp-projectStart'))

            elif page2Send == 'rsp-selectProject.html':
                return render_template("home/" + template,
                                       projects=dbquery.getListDictResultset(
                                           f"select descProjeto as caption, id from Projeto p "
                                           f"where idUser = {current_user.id}"
                                           f"order by descProjeto"),
                                       **helper.getFormText('rsp-selectProject'))

            elif page2Send == 'rsp-projectName.html':
                if 'id' in request.args.keys():
                    projectId = int(request.args['id'])
                if projectId > -1:
                    projectName = dbquery.getValues(f"select descProjeto from Projeto where id = {projectId}")
                    session['_projeto_id'] = projectId
                    session['_operation'] = 'changingProject'
                else:
                    projectName = ''
                    session['_operation'] = 'includingProject'
                return render_template("home/rsp-projectName.html",
                                       projectNameValue=projectName,
                                       **helper.getFormText('rsp-projectName'))

            elif page2Send == 'rsp-locationMethodSelect.html':
                formItems = helper.getFormText('rsp-locationMethodSelect')
                if session['_operation'] == 'changingProject':
                    lat, lon = dbquery.getValues(f"select lat, lon from Projeto where id = {session['_projeto_id']}")
                    formItems = {**{'selectedcountyFitofisionomy': int(lat is None),
                                 'selectedlatLong': int(lat is not None)},
                                 **formItems}
                else:
                    formItems = {**{'selectedcountyFitofisionomy': 0,
                                 'selectedlatLong': 0},
                                 **formItems}
                return render_template("home/" + template, **formItems)

            elif page2Send == 'rsp-locationCountyFitofisionomy.html':
                if session['_operation'] == 'changingProject':
                    idMunicipioidFito = dbquery.getValues(
                        f"select coalesce(idMunicipio, -1) as idMunicipio, "
                        f"coalesce(idMunicipioFito, -1) as idFitoFisionomia "
                        f"from Projeto p "
                        f"inner join MunicipioFito mf "
                        f"on p.idMunicipioFito = mf.id "
                        f"where p.id = {session['_projeto_id']}")
                    idMunicipio, idFitofisionomia = (-1, -1) if idMunicipioidFito is None else idMunicipioidFito
                else:
                    idMunicipio, idFitofisionomia = (-1, -1)

                municipios = ui_projectSupport.getListaMunicipios()
                fito_municipios = ui_projectSupport.getListaFito(idMunicipio)
                formText = helper.getFormText('rsp-locationCountyFitofisionomy')
                strMunicipios, strFitoMunicipios = '', ''
                for key, value in municipios.items():
                    selected = '  selected="selected" ' if key == idMunicipio else ' '
                    strMunicipios += f'<option{selected}value="{key}">{value}</option>\n'
                for key, value in fito_municipios.items():
                    selected = '  selected="selected" ' if key == idFitofisionomia else ''
                    strFitoMunicipios += f'<option{selected}value="{key}">{value}</option>\n'

                return render_template("home/" + template,
                                       idMunicipio=idMunicipio,
                                       idFitofisionomia=idFitofisionomia,
                                       municipios=strMunicipios
                                       , fito_municipios=strFitoMunicipios
                                       , **formText
                                       )

            elif page2Send == 'rsp-locationLatLon.html':
                lat, lon = dbquery.getValues(f"select coalesce(lat,'') as lat, "
                                             f"coalesce(lon,'') as lon "
                                             f"from Projeto where id = {session['_projeto_id']}")
                return render_template("home/" + template,
                                       lat=lat, lon=lon,
                                       **helper.getFormText('rsp-locationLatLon'))

            elif page2Send == 'rsp-locationCAR.html':
                return render_template("home/" + template,
                                       **helper.getFormText('rsp-locationCAR'))

            elif page2Send == 'rsp-areas.html':
                avalilableCombinations = dbquery.getValues(
                    f"""select count(mf.id)
  from combinacao c
       inner join Municipio m on m.idRegiaoEco = c.idRegiaoEco
       inner join MunicipioFito mf on
                  mf.idMunicipio = m.id and
                  mf.idFitoFisionomia = c.idFitoFisionomia
       inner join Projeto p on
                  mf.id = p.idMunicipioFito
  where p.id = {session['_projeto_id']}""")
                if avalilableCombinations == 0:
                    return render_template("home/rsp-theresNoCombinations.html",
                                           **helper.getFormText('rsp-theresNoCombinations'))
                if session['_operation'] == 'changingProject':
                    areaProjeto, areaPropriedade = dbquery.getValues(
                        f"select AreaProjeto, AreaPropriedade from Projeto "
                        f"where id = {session['_projeto_id']}")
                else:
                    areaProjeto, areaPropriedade = (None, None)
                return render_template("home/rsp-areas.html",
                                       areaProjeto = areaProjeto,
                                       areaPropriedade = areaPropriedade,
                                       **helper.getFormText('rsp-areas'))

            elif page2Send == 'rsp-goal.html':
                # Opção APP só está disponível para propriedades com área menor que 4 módulos fiscais do município
                removeAPPoption = dbquery.getValues(
                    "select count(1) from Projeto p "
                    "inner join MunicipioFito mf "
                    "on p.idMunicipioFito = mf.id "
                    "inner join Municipio m "
                    "on mf.idMunicipio = m.id "
                   f"where p.id = {session['_projeto_id']} "
                    "and p.AreaPropriedade > m.moduloFiscal * 4")
                goals=dbquery.getListDictResultset(
                                            "select f.desFinalidade as caption, f.id, f.help as hint, "
                                            f"case "
                                            f"        when f.id = idFinalidade then 1 "
                                            f"        else 0 "
                                            f"end as selected "
                                            f"from Finalidade f "
                                            f"inner join Projeto p "
                                            f"on p.id = {session['_projeto_id']} "
                                            f"{'where f.id <> 3' if removeAPPoption > 0 else ''} "
                                            f"order by orderby"
                                        )

                return render_template("home/" + template,
                                           goals=goals
                                       , **helper.getFormText('rsp-goal'))

            elif page2Send == 'rsp-plantDistribution.html':
                # TODO: number of número de módulos fiscais validation
                idFinalidade = request.args.get('id')
                dbquery.executeSQL(f"update Projeto set idFinalidade = {idFinalidade} "
                                   f"where id = {session['_projeto_id']}")
                distributionOptions = ui_plantdistribution.getPlantDistribution(session['_projeto_id'])
                return render_template("home/" + template,
                                       options=distributionOptions,
                                       **helper.getFormText('rsp-plantDistribution'))

            elif page2Send == 'rsp-relief.html':
                idModeloPlantio = request.args.get('id')
                dbquery.executeSQL(f"update Projeto set idModeloPlantio = {idModeloPlantio} "
                                   f"where id = {session['_projeto_id']}")
                idTopografia = dbquery.getValues(f"select idTopografia from Projeto where id = {session['_projeto_id']}")
                options = [
                    {'caption': 'Terreno Plano', 'id': 1, 'fileName': 'wzd-terrenoPlano.png'},
                    {'caption': 'Terreno Suave Ondulado', 'id': 2, 'fileName': 'wzd-terrenoSuaveOndulado.png'},
                    {'caption': 'Terreno Ondulado', 'id': 3, 'fileName': 'wzd-terrenoOndulado.png'},
                    {'caption': 'Terreno Montanhoso', 'id': 4, 'fileName': 'wzd-terrenoMontanhoso.png'}
                ]
                for option in options:
                    option['selected'] = int(option['id'] == idTopografia)
                return render_template("home/" + template,
                                       options=json.dumps(options),
                                       **helper.getFormText('rsp-relief'))

            elif page2Send == "rsp-mecanization.html":
                idTopografia = request.args.get('id')
                dbquery.executeSQL(f"update Projeto set idTopografia = {idTopografia} "
                                   f"where id = {session['_projeto_id']}")

                return render_template("home/" + template,
                                       mecanization=dbquery.getListDictResultset(
                                           "select nomeMecanizacao as caption, mn.id, help as hint,"
                                           "case "
                                                "when mn.id = p.idMecanizacaoNivel then 1 "
                                                "else 0 "
                                            "end as selected "
                                            "from MecanizacaoNivel mn "
                                            "left join Projeto p "
                                            "on 1=1 "
                                            f"where p.id = {session['_projeto_id']}"),
                                       **helper.getFormText('rsp-mecanization'))

            elif page2Send == 'rsp-combinations.html':
                # return render_template("home/rsp-relief.html", segment="rsp-relief.html")
                idMecanizacaoNivel = request.args.get('id')

                dbquery.executeSQL(f"update Projeto set idMecanizacaoNivel = {idMecanizacaoNivel} "
                                   f"where id = {session['_projeto_id']}")

                combinations, strips, noData = ui_combination.getCombinations(session['_projeto_id'])
                return render_template("home/" + template,
                                       strips=strips,
                                       combinations=combinations,
                                       noData=noData,
                                       **helper.getFormText('rsp-combinations'))

            elif page2Send == 'rsp-projectEnd.html':
                selectedCombinations = ui_projectEnd.formatCombinations(request.args['id'],'-',"','",4)
                ui_projectEnd.updateProjectCombinationData(session['_projeto_id'], selectedCombinations)
                dfFinance, tir, investimento, payback = ui_projectEnd.CalculateFinanceData(session['_projeto_id'])
                cashFlowJSON = ui_projectEnd.cashFlowChart(dfFinance)
                ui_projectEnd.updateProjectFinanceData(session['_projeto_id'], tir, investimento, payback)
                projectData = ui_projectEnd.getProjectData(session['_projeto_id'])

                return render_template("home/" + template,
                                       cashFlowJSON=cashFlowJSON,
                                       **projectData,
                                       **helper.getFormText('rsp-projectEnd'))

            elif page2Send == 'rsp-sendSpreadsheet.html':
                user_email = dbquery.getValues("select email from users u "
                                               "inner join Projeto p "
                                               "on p.idUser = u.id "
                                               f"where p.id = {session['_projeto_id']}")
                return render_template("home/" + template,
                                       user_email = user_email,
                                       **helper.getFormText('rsp-sendSpreadsheet'))

            elif page2Send == 'rsp-wizardEnd.html':
                return render_template("home/" + template,
                                       **helper.getFormText('rsp-wizardEnd'))

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
    except Exception as e:
        return render_template('home/page-500.html', errorMsg=str(e)), 500
