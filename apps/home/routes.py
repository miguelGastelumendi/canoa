# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.home import ui_map, ui_plantdistribution, dbquery
from flask import session
import re


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
    idMunicipio = int(args.get('idMunicipio'))
    idFito = int(args.get('idFito')) if callerID == 'fito_ecologica'or callerID is None else -1
    latlong = args.get('latlong')
    CAR = args.get('CAR')
    if endpoint == 'updateFormData':
        # else
        return ui_map.getMapFitoMunicipio(callerID,
                                          idMunicipio,
                                          idFito,
                                          latlong,
                                          CAR)
    elif endpoint == 'saveProject':
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
            segment = get_segment(request)
            if segment == 'rsp-projeto_localizacao.html':
                return render_template("home/" + template,
                                       municipios=ui_map.getListaMunicipios()
                                       , fito_municipios=ui_map.getListaFito(None)
                                       #, map=ui_map.getMapSP()
                                       )
            elif segment.startswith('rsp-plantDistribution'):
            # TODO: number of número de módulos fiscais validation
                finalidade_id = re.findall(r'\(.*?\)', template)[0].replace('(', '').replace(')', '')
                dbquery.executeSQL(f"update ProjetoPreferencias set idFinalidade = {finalidade_id} "
                                   f"where idProjeto = {session['_projeto_id']}")
                template = template[0:template.find('(')] + '.html'
                segment = segment[0:template.find('(')]+'.html'
                render_template("home/" +template, segment=segment)
            # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
