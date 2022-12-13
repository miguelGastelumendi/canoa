# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.home import ui_map

@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')

@blueprint.route('/callback/<endpoint>')
@login_required
def route_callback(endpoint):
    args = request.args
    if endpoint == 'getMunicipioFito':
        idMunicipio = int(args.get('idMunicipio'))
        idFito = int(args.get('idFito'))
        latlong = args.get('latlong')
        CAR = args.get('CAR')
        return ui_map.getMapFitoMunicipio(idMunicipio,
                                          idFito,
                                          latlong,
                                          CAR)

@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if template.endswith('.html'):
            # Detect the current page
            segment = get_segment(request)
            if segment == 'ui-map.html':
                return render_template("home/" + template,
                                       municipios=ui_map.getListaMunicipios(),
                                       fito_municipios=ui_map.getListaFito(None)
                                       )
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
