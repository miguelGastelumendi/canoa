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
        extent = centroid_extent_polytype[2].replace('(', '').replace(',', '').split(' ')
        max_bound = max(abs(float(extent[1]) - float(extent[3])),
                        abs(float(extent[2]) - float(extent[6]))) * 111  # km/degree
        zoom = 12.0 - np.log(max_bound)
    else:
        zoom = 12.0
    return gjson, centroid, zoom


def getListaMunicipios():
    return dbquery.getDictResultset("select id, NomeMunicipio from Municipio "
                                    "order by NomeMunicipio")


def getListaFito(idMunicipio: int):
    return dbquery.getDictResultset(
        f"select mf.id,descFitoFisionomia as Fitofisionomia "
        f"from MunicipioFito mf "
        f"inner join FitoFisionomia ff "
        f"on mf.idFitoFisionomia = ff.id "
        f"where {' 0=1' if idMunicipio is None else f'idMunicipio = {idMunicipio}'} "
        f"order by 2")


def getCAR(CAR: str):
    df = dbquery.getDataframeResultset(f"select OBJECTID as id, CAR from CAR "
                                       f"where CAR = '{CAR}'")
    features = [json.loads(x) for x in dbquery.getListResultset(
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
    features = [json.loads(x) for x in dbquery.getListResultset(
        f"select geomText from Municipio where id = {idMunicipio}")]
    centroid_extent_polytype = dbquery.executeSQL(
        f"select Centroid.STY as Longitude, Centroid.STX as Latitude, extent, geometrytype from "
        f"(select geom.STCentroid() as Centroid, geom.STEnvelope().STAsText() as extent "
        f",geom.STGeometryType() as geometrytype "
        f"from Municipio where id = {idMunicipio}) a").first()
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


def getSP():
    df = dbquery.getDataframeResultset(
        f"select id,Nome "
        f"from SP ")
    features = [json.loads(x) for x in dbquery.getListResultset(
        f"select geomText from SP ")]
    centroid_extent_polytype = dbquery.executeSQL(
        f"select Centroid.STY as Longitude, Centroid.STX as Latitude, extent, geometrytype from "
        f"(select geom.STCentroid() as Centroid, geom.STEnvelope().STAsText() as extent "
        f",geom.STGeometryType() as geometrytype "
        f"from SP) a").first()
    gjson, centroid, zoom = getGJson(centroid_extent_polytype, features)
    return df, gjson, centroid, zoom


def getFitoMunicipio(callerID: str, idMunicipio:
int, idFito: int, latlong: str, CAR: str):
    if CAR != '':
        whereFito = (f"where mf.id in (select mf.id from car c \n"
                     f"inner join MunicipioFito mf \n"
                     f"on c.idMunicipio = mf.idMunicipio \n"
                     f"where car = '{CAR}' \n"
                     f"and c.geom.STIntersects(mf.geom) = 1)")
        area = f"{dbquery.getValueFromDb(f'select area from CAR where car = {CAR}'):.4f}".replace('.', ',')
    elif latlong != '':
        lat, long = latlong.split(' ')
        lat = lat.replace(',', '.').replace('S', '')
        long = long.replace(',', '.').replace('S', '')
        if not lat.startswith('-'):
            lat = '-' + lat
        if not long.startswith('-'):
            long = '-' + long
        whereFito = f"where mf.geom.STIntersects((geometry::STPointFromText('POINT ({long} {lat})', 4326)))=1"
        area = ''
    else:
        whereFito = (f"where mf.idMunicipio = {idMunicipio} " +
                     (f"and mf.id = {idFito}" if idFito > -1 else ""))
        area = ''
    fito = dbquery.getDataframeResultset(
        f"select mf.id,concat(m.nomeMunicipio,'/',descFitoFisionomia) as label,ff.color "
        f"from MunicipioFito mf "
        f"inner join Municipio m "
        f"on mf.idMunicipio = m.id "
        f"inner join FitoFisionomia ff "
        f"on mf.idFitoFisionomia = ff.id "
        f"{whereFito} ")
    features = [json.loads(x) for x in dbquery.getListResultset(
        f"select geomtext from MunicipioFito mf {whereFito}")]
    centroid_extent_polytype = dbquery.executeSQL(
        f"select Centroid.STY as Longitude, Centroid.STX as Latitude, extent, geometrytype from "
        f"(select geom.STCentroid() as Centroid, geom.STEnvelope().STAsText() as extent "
        f",geom.STGeometryType() as geometrytype "
        f"from MunicipioFito mf {whereFito}) a").first()
    color = fito.set_index('id').to_dict()['color']
    gjson, centroid, zoom = getGJson(centroid_extent_polytype, features)
    return fito, gjson, centroid, zoom, color, area


def getMapFitoMunicipio(callerID: str,
                        idMunicipio: int,
                        idFito: int,
                        latlong: str,
                        CAR: str):
    fito, geo, centroid, zoom, color, area = getFitoMunicipio(callerID,
                                                              idMunicipio, idFito, latlong, CAR)
    fig = px.choropleth_mapbox(fito, geojson=geo, color=fito.color.tolist(),
                               locations=fito.id, featureidkey="properties.id",
                               center=centroid,
                               hover_name=fito.label.tolist(),
                               color_discrete_map="identity",
                               hover_data={'id': False},
                               mapbox_style="carto-positron", zoom=zoom,
                               opacity=0.4)
    fig.update_layout(
        showlegend=False)

    graphJSON = json.dumps({'Map': json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder),
                            'FitoMunicipio': json.dumps(getListaFito(idMunicipio), cls=plotly.utils.PlotlyJSONEncoder),
                            'Area': area})
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


def getMapSP():
    SP, geo, centroid, zoom = getSP()
    fig = px.choropleth_mapbox(SP, geojson=geo,
                               locations=SP.id, featureidkey="properties.id",
                               center=centroid,
                               hover_name=SP.Nome.tolist(), hover_data={'id': False},
                               mapbox_style="carto-positron", zoom=zoom,
                               opacity=0.4)
    graphJSON = json.dumps({'Map': json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)})
    return graphJSON


def saveProject(userId: str,
                projectName: str,
                projectArea,
                propertyArea,
                idFito: int,
                latlong: str,
                CAR: str):
    # dbquery.executeSQL("delete from ProjetoPreferencias; delete from Projeto")

    dbquery.executeSQL(f"INSERT INTO Projeto(idUser, descProjeto, CAR, idMunicipioFito, AreaProjeto, AreaPropriedade,"
                       f" dtCriacao, dtAtualizacao) "
                       f"VALUES ({userId}, '{projectName}', '{CAR}', {idFito}, {projectArea}, {propertyArea},"
                       f"GETDATE(), GETDATE())")
    project_id = dbquery.getLastId('Projeto')
    return project_id

def getProjectData(projectId):
    pass
