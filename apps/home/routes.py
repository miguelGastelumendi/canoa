# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
import apps.home.ui_map as ui_map
import apps.home.ui_plantdistribution as ui_plantdistribution
import apps.home.dbquery as dbquery
import apps.home.ui_combination as ui_combination
from flask import session
from apps.home import helper


@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')

@blueprint.route('/callback/<endpoint>')
@login_required
def route_callback(endpoint):
    if endpoint == 'getDistribution':
       return ui_plantdistribution.getPlantDistribution(session['_projeto_id'])
    args = request.args
    callerID = args.get('callerID')
    if callerID == 'mapSP':
        return ui_map.getMapSP()
    idFito = int(args.get('idFito')) if callerID in ['fito_ecologica', 'saveProject'] else -1
    latlong = args.get('latlong')
    CAR = args.get('CAR')
    if endpoint == 'updateFormData':
        idMunicipio = int(args.get('idMunicipio'))
        return ui_map.getMapFitoMunicipio(callerID,
                                          idMunicipio,
                                          idFito,
                                          latlong,
                                          CAR)
    elif endpoint == 'saveProject':
        projectName = args.get('ProjectName')
        if projectName == '':
            session['_projeto_id'] = 18
            return "Ok"
        projeto_id=ui_map.saveProject(session['_user_id'],
                                  args.get('ProjectName'),
                                  args.get('ProjectArea'),
                                  args.get('PropertyArea'),
                                  idFito,
                                  latlong,
                                  CAR)
        session['_projeto_id'] = projeto_id
    return "Ok"

@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if template.find('.html') > -1:
            # Detect the current page
            segment = helper.get_segment(request)
            # if segment.startswith('testeJinja'):
            if segment.startswith('rsp-combinations'):
                # return render_template("home/testeJinja.html",
                combinations, strips = ui_combination.getCombinations(session['_projeto_id'])
                return render_template("home/" + template,
                                       strips=strips,
                                       combinations=combinations)
            if segment == 'rsp-projeto_localizacao.html':
                return render_template("home/" + template,
                                       municipios=ui_map.getListaMunicipios()
                                       , fito_municipios=ui_map.getListaFito(None)
                                       #, map=ui_map.getMapSP()
                                       )
            elif segment == 'rsp-plantDistribution.html':
            # TODO: number of número de módulos fiscais validation
                idFinalidade = request.args.get('id')
                dbquery.executeSQL(f"update ProjetoPreferencias set idFinalidade = {idFinalidade} "
                                   f"where idProjeto = {session['_projeto_id']}")
                render_template("home/" +template, segment=segment)
            elif segment == 'rsp-relief.html':
                idTopografia = request.args.get('id')
                dbquery.executeSQL(f"update ProjetoPreferencias set idTopografia = {idTopografia} "
                                   f"where idProjeto = {session['_projeto_id']}")
                render_template("home/" +template, segment=segment)

        return render_template("home/" + template, segment=helper.get_segment(template))
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
    except Exception as e:
        return render_template('home/page-500.html'), 500

