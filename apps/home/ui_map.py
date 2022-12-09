import plotly
import plotly.express as px
import json
import numpy as np
import apps.home.dbquery as dbquery
import apps.config as config

def getGJson(centroid_extent_polytype, features):
    if centroid_extent_polytype[3] == 'MultiPolygon':
        for feature in features:
            if not isinstance(feature['geometry']['coordinates'][0][0][0], list):
                feature['geometry']['coordinates'] = [feature['geometry']['coordinates']]
    gjson = {'type': 'FeatureCollection',
             'features': features}
    centroid = {"lat": centroid_extent_polytype[0], "lon": centroid_extent_polytype[1]}
    if centroid_extent_polytype[2] is not None:
        extent = centroid_extent_polytype[2].replace('(', '').replace(',','').split(' ')
        max_bound = max(abs(float(extent[1]) - float(extent[3])), abs(float(extent[2]) - float(extent[6]))) * 111 # km/degree
        zoom = 13.5 - np.log(max_bound)
    else:
        zoom = 13.5
    return gjson, centroid, zoom

def getListaMunicipios():
    return dbquery.getDictResultset("select id, NomeMunicipio from Municipio "
                                    "order by NomeMunicipio")

def getListaFito(idMunicipio: int):
    return dbquery.getDictResultset(
        f"select mf.id,descFitoFisionomia "
        f"from MunicipioFito mf "
        f"inner join FitoFisionomia ff "
        f"on mf.idFitoFisionomia = ff.id "
        f"where {' 0=1' if idMunicipio is None else f'idMunicipio = {idMunicipio}'}")

def getCAR(CAR : str):
    df = dbquery.getDataframeResultset(f"select OBJECTID as id, CAR from CAR "
                                  f"where CAR = '{CAR}'")
    features=[json.loads(x) for x in dbquery.getListResultset(
        f"select geomtext from CAR where CAR = '{CAR}'")]
    centroid_extent_polytype = dbquery.executeSQL(
        f"select Centroid.STY as Longitude, Centroid.STX as Latitude, extent, geometrytype from "
        f"(select geom.STCentroid() as Centroid, geom.STEnvelope().STAsText() as extent "
        f",geom.STGeometryType() as geometrytype "
        f"from CAR where CAR = '{CAR}') a").first()
    gjson, centroid, zoom = getGJson(centroid_extent_polytype, features)
    return df, gjson, centroid, zoom

def getMunicipio(idMunicipio: int):
    df = dbquery.getDataframeResultset(
        f"select id,NomeMunicipio "
        f"from Municipio "
        f"where id = {idMunicipio}")
    features=[json.loads(x) for x in dbquery.getListResultset(
        f"select geomText from Municipio where id = {idMunicipio}")]
    centroid_extent_polytype = dbquery.executeSQL(
        f"select Centroid.STY as Longitude, Centroid.STX as Latitude, extent, geometrytype from "
        f"(select geom.STCentroid() as Centroid, geom.STEnvelope().STAsText() as extent "
        f",geom.STGeometryType() as geometrytype "
        f"from Municipio where idMunicipio = {idMunicipio}) a").first()
    gjson, centroid, zoom = getGJson(centroid_extent_polytype, features)
    return df, gjson, centroid, zoom

def getMapMunicipio(idMunicipio: int):
    municipio, geo, centroid, zoom = getMunicipio(idMunicipio)
    fig = px.choropleth_mapbox(municipio, geojson=geo,
                               locations=municipio.id, featureidkey="properties.id",
                               center=centroid,
                               hover_name=municipio.NomeMunicipio.tolist(), hover_data={'id': False},
                               mapbox_style="carto-positron", zoom=zoom,
                               opacity=0.4)
    # fig.update_layout(
    #     mapbox_style="white-bg",
    #     showlegend=False)
    # fig.update_layout(coloraxis_showscale=False)
    graphJSON = json.dumps({'Map': json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder),
                            'Fito': json.dumps(getListaFito(idMunicipio), cls=plotly.utils.PlotlyJSONEncoder)})
    return graphJSON
def getFitoMunicipio(idMunicipio: int):
    df = dbquery.getDataframeResultset(
        f"select mf.id,descFitoFisionomia "
        f"from MunicipioFito mf "
        f"inner join FitoFisionomia ff "
        f"on mf.idFitoFisionomia = ff.id "
        f"where idMunicipio = {idMunicipio}")
    features=[json.loads(x) for x in dbquery.getListResultset(
        f"select geomtext from MunicipioFito where idMunicipio = {idMunicipio}")]
    centroid_extent_polytype = dbquery.executeSQL(
        f"select Centroid.STY as Longitude, Centroid.STX as Latitude, extent, geometrytype from "
        f"(select geom.STCentroid() as Centroid, geom.STEnvelope().STAsText() as extent "
        f",geom.STGeometryType() as geometrytype "
        f"from MunicipioFito where idMunicipio = {idMunicipio}) a").first()
    gjson, centroid, zoom = getGJson(centroid_extent_polytype, features)
    return df, gjson, centroid, zoom

def getMapFitoMunicipio(idMunicipio: int):
    fito, geo, centroid, zoom = getFitoMunicipio(idMunicipio)
    fig = px.choropleth_mapbox(fito, geojson=geo,
                               locations=fito.id, featureidkey="properties.id",
                               center=centroid,
                               hover_name=fito.id.tolist(), hover_data={'id': False},
                               mapbox_style="carto-positron", zoom=zoom,
                               opacity=0.4)
    # fig.update_layout(
    #     mapbox_style="white-bg",
    #     showlegend=False)
    # fig.update_layout(coloraxis_showscale=False)
    graphJSON = json.dumps({'Map': json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder),
                            'FitoMunicipio': json.dumps(getListaFito(idMunicipio), cls=plotly.utils.PlotlyJSONEncoder)})
    return graphJSON

def getMapCAR(pCAR: str = ''):
    CAR, geo, centroid, zoom = getCAR(pCAR)
    fig = px.choropleth_mapbox(CAR, geojson=geo,
                               locations=CAR.id, featureidkey="properties.id",
                               center=centroid,
                               hover_name=CAR.CAR.tolist(), hover_data={'id': False},
                               mapbox_style="carto-positron", zoom=zoom,
                               opacity=0.4)
    # fig.update_layout(
    #     mapbox_style="white-bg",
    #     showlegend=False)
    # fig.update_layout(coloraxis_showscale=False)
    graphJSON = json.dumps({'Map': json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)})
    return graphJSON
