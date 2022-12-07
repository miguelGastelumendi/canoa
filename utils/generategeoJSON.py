import dbquery
import json

def updateMunicipio():
    sqlmun="select id,NomeMunicipio, dbo.geomToGeoJSON(geom, 3) as geom,"
    "case "
    "   when CharIndex('Multi',geom.STAsText()) = 1 then 'MultiPolygon'"
    "   else 'Polygon' "
    "end polytype "
    "from Municipio "
    "--where id = 281 \n"
    "order by 1"
    df = dbquery.getDataframeResultset(sqlmun)
    for _,row in df.iterrows():
        dic = json.loads(row.geom)
        municipio=row.NomeMunicipio
        newdict = {"type": "Feature",
                   "geometry" : {"type": f"{row.polytype}",
                   'coordinates': dic['coordinates']},
                   'properties': {'id': row.id,
                                  'NomeMunicipio': municipio.replace("'","''")}
                   }
        sdic = json.dumps(newdict)
        dbquery.executeSQL(f"UPDATE Municipio set geomText = '{sdic}' where id = {row.id}")
        print(_,row.id)

def updateCAR():
    ids = dbquery.getDataframeResultset('select OBJECTID from CAR where OBJECTID >= 64159 and lengthGeomAsText < 10000 order by 1')
    i=0
    #count=dbquery.getValueFromDb('select top 123 count(1) from CAR')
    count = len(ids)
    for _,row in ids.iterrows():
        if i == 0:
            min_id = row.OBJECTID
            i+=1
        elif (i == 1000) or (_ == count):
            where = f'where OBJECTID >= {min_id} and OBJECTID <= {row.OBJECTID} and lengthGeomAsText < 10000'
            df = dbquery.getDataframeResultset("select OBJECTID, dbo.geomToGeoJSON(geom, 8) as geom,"
            "case "
            "   when CharIndex('Multi',geom.STAsText()) = 1 then 'MultiPolygon'"
            "   else 'Polygon' "
            "end polytype "
            f"from CAR {where}"
             )
            for _,row2 in df.iterrows():
                if row2.geom is None:
                    continue
                dic = json.loads(row2.geom)
                newdict = {"type": "Feature",
                           "geometry" : {"type": f"{row2.polytype}",
                           'coordinates': dic['coordinates']},
                           'properties': {'id': row2.OBJECTID}
                           }
                sdic = json.dumps(newdict)
                dbquery.executeSQL(f"UPDATE CAR set geomText = '{sdic}' where OBJECTID = {row2.OBJECTID}")
                print(_,row2.OBJECTID)
            i=0
        else:
            i+=1


if __name__ == "__main__":
    updateCAR()
    print('Done!')
