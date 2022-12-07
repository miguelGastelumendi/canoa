import plotly
import plotly.express as px
import json
import numpy as np
import apps.home.dbquery as dbquery

def getMunicipio(id : str = ''):
    where = f'where id = {id}' if id != '' else ''
    df = dbquery.getDataframeResultset(f"select id, nomeMunicipio from Municipio "
                                  f"{where}")
    features=[json.loads(x) for x in dbquery.getListResultset(f"select geomtext from Municipio {where}")]
    for feature in features:
        if not isinstance(feature['geometry']['coordinates'][0][0][0], list):
            feature['geometry']['coordinates'] = [feature['geometry']['coordinates']]
    gjson = {'type': 'FeatureCollection',
             'features': features}

    values = None
    centroid = None
    if where == '':
        centroid = [-22.265816380698734, -48.72884588141674]
        values = ['-53.110111532', '-25.3123209497299', '-44.1613651636666', '-19.7796557956015']
    else:
        centroid = dbquery.executeSQL(
            f"select avg(Centroid.STY) as Longitude, avg(Centroid.STX) as Latidude from "
            f"(select geom.STCentroid() as Centroid from Municipio {where}) a").first()
        extent = dbquery.executeSQL(f"select st_extent(geom) from Municipio {where}").first()
        if extent[0] is not None: # SP state extent
            values = extent[0].replace(',', ' ').replace('(', ' ').replace(')', ' ').split(' ')[1:]
    if values is not None:
        max_bound = max(abs(float(values[0]) - float(values[2])), abs(float(values[1]) - float(values[3]))) * 111 # km/degree
        zoom = 13.5 - np.log(max_bound)
    else:
        zoom = 13.5
    return df, gjson, {"lat": centroid[1], "lon": centroid[0]}, zoom

def getFigMunicipio(id: str = ''):
    municipio, geo, centroid, zoom = getMunicipio(id)
    fig = px.choropleth_mapbox(municipio, geojson=geo,
                               locations=municipio.id, featureidkey="properties.id",
                               center=centroid,
                               hover_name=municipio.nomeMunicipio.tolist(), hover_data={'id': False},
                               mapbox_style="carto-positron", zoom=zoom,
                               opacity=0.4)

    fig.update_layout(
        mapbox_style="white-bg",
        showlegend=False)
    fig.update_layout(coloraxis_showscale=False)
    graphJSON = json.dumps({'Map': json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)})
    return graphJSON
