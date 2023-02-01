# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
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


@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')


@blueprint.route('/callback/<endpoint>')
@login_required
def route_callback(endpoint):
    args = request.args
    callerID = args.get('callerID')
    if callerID == 'mapSP':
        return ui_projectSupport.getMapSP()
    if endpoint == 'projectName':
        if not '_projeto_id' in session.keys() or session['_projeto_id'] == -1:
            session['_projeto_id'] = ui_projectSupport.createProject(current_user.id, request.args['projectName'])
        else:
            try:
                ui_projectSupport.updateProject(session['_projeto_id'], descProjeto=request.args['projectName'])
            except Exception as e:
                if '23000' in re.split('\W+', e.args[0]):
                    return helper.getErrorMessage('projectNameMustBeUnique')
        return "Ok"
    if endpoint == 'rsp-areas':
        if not '_projeto_id' in session.keys() or session['_projeto_id'] == -1:
            session['_projeto_id'] = ui_projectSupport.createProject(current_user.id, request.args['rsp-areas'])
        else:
            try:
                ui_projectSupport.updateProject(session['_projeto_id'], descProjeto=request.args['rsp-areas'])
            except Exception as e:
                if '23000' in re.split('\W+', e.args[0]):
                    return helper.getErrorMessage('projectNameMustBeUnique')
        return "Ok"
    if endpoint == 'locationCAR':
        return ui_projectSupport.getMapCAR(request.args.get('CAR'))
    if endpoint == 'locationLatLon':
        return ui_projectSupport.getMapLatLon(request.args.get('lat'), request.args.get('lon'))
    if endpoint == 'getDistribution':
            return ui_plantdistribution.getPlantDistribution(session['_projeto_id'])

    idFito = int(args.get('idFito')) if callerID in ['fito_ecologica', 'saveProject'] else -1
    latlong = args.get('latlong')
    CAR = args.get('CAR')
    if endpoint == 'updateFormData':
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
                                            **{'idMunicipioFito': idFito, 'CAR': CAR})
            return ui_projectSupport.getMapFitoMunicipio(callerID,
                                                         idMunicipio,
                                                         idFito,
                                                         latlong,
                                                         CAR)


    elif endpoint == 'help':
        return helper.getHelpText(args.get('id'))
    return "Ok"


@blueprint.route('/<template>')
@login_required
def route_template(template):
    projectId = -1
    try:
        if template.find('.html') > -1:
            # Detect the current page
            segment = helper.get_segment(request)
            # if segment.startswith('testeJinja'):
            if segment == 'rsp-projectStart.html':
                session['_projeto_id'] = -1
                return render_template("home/" + template,
                                       **helper.getFormText('rsp-projectStart'))

            if segment == 'rsp-selectProject.html':
                return render_template("home/" + template,
                                       projects=dbquery.getListDictResultset(
                                           f"select descProjeto as caption, id from Projeto p "
                                           f"where idUser = {current_user.id}"
                                           f"order by descProjeto"),
                                       **helper.getFormText('rsp-selectProject'))

            if segment == 'rsp-projectName.html':
                if 'id' in request.args.keys():
                    projectId = int(request.args['id'])
                if projectId > -1:
                    projectName = dbquery.getValueFromDb(f"select descProjeto from Projeto where id = {projectId}")
                    session['_projeto_id'] = projectId
                else:
                    projectName = ''
                return render_template("home/rsp-projectName.html",
                                       projectNameValue=projectName,
                                       **helper.getFormText('rsp-projectName'))

            if segment == 'rsp-areas.html':
                if 'id' in request.args.keys():
                    projectId = int(request.args['id'])
                if projectId > -1:
                    projectName = dbquery.getValueFromDb(f"select descProjeto from Projeto where id = {projectId}")
                    session['_projeto_id'] = projectId
                else:
                    projectName = ''
                return render_template("home/rsp-areas.html",
                                       projectNameValue=projectName,
                                       **helper.getFormText('rsp-areas'))

            if segment == 'rsp-locationMethodSelect.html':
                return render_template("home/" + template,
                                       **helper.getFormText('rsp-locationMethodSelect'))

            if segment == 'rsp-locationCountyFitofisionomy.html':
                return render_template("home/" + template,
                                       municipios=ui_projectSupport.getListaMunicipios()
                                       , fito_municipios=ui_projectSupport.getListaFito(None)
                                       , **helper.getFormText('rsp-locationCountyFitofisionomy')
                                       )

            if segment == 'rsp-locationLatLon.html':
                return render_template("home/" + template,
                                       **helper.getFormText('rsp-locationLatLon'))

            if segment == 'rsp-locationCAR.html':
                return render_template("home/" + template,
                                       **helper.getFormText('rsp-locationCAR'))

            elif segment == 'rsp-goal.html':
                return render_template("home/" + template,
                                       goals=dbquery.getListDictResultset(
                                           f"select desFinalidade as caption, id "  # desFinalidade: typo
                                           f"from Finalidade "
                                           f"order by orderby")
                                       , **helper.getFormText('rsp-goal'))

            elif segment == 'rsp-plantDistribution.html':
                # TODO: number of número de módulos fiscais validation
                idFinalidade = request.args.get('id')
                dbquery.executeSQL(f"update Projeto set idFinalidade = {idFinalidade} "
                                   f"where id = {session['_projeto_id']}")
                return render_template("home/" + template
                                       , **helper.getFormText('rsp-plantDistribution'))


            elif segment == 'rsp-relief.html':
                idModeloPlantio = request.args.get('id')
                dbquery.executeSQL(f"update Projeto set idModeloPlantio = {idModeloPlantio} "
                                   f"where id = {session['_projeto_id']}")
                return render_template("home/" + template
                                       , **helper.getFormText('rsp-relief'))

            elif segment == "rsp-mecanization.html":
                idTopografia = request.args.get('id')
                dbquery.executeSQL(f"update Projeto set idTopografia = {idTopografia} "
                                   f"where id = {session['_projeto_id']}")

                return render_template("home/" + template,
                                       mecanization=dbquery.getListDictResultset(
                                           f"select nomeMecanizacao as caption, id "  # desFinalidade: typo
                                           f"from MecanizacaoNivel "),
                                       **helper.getFormText('rsp-mecanization'))

            elif segment == 'rsp-combinations.html':
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

            elif segment == 'rsp-projectEnd.html':
                #                ui_projectData.updateProjectData(session['_projeto_id'], request.args['id'])
                projectData, combinations = ui_projectEnd.getProjectData(session['_projeto_id'], request.args['id'])
                return render_template("home/" + template, combinations=combinations, **projectData,
                                       **helper.getFormText('rsp-projectEnd'))

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
    except Exception as e:
        return render_template('home/page-500.html', errorMsg=str(e)), 500
