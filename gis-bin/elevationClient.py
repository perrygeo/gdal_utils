#!/usr/bin/env python
import urllib
import ogr
from BeautifulSoup import BeautifulStoneSoup

#service_base_url = "http://gisdata.usgs.gov/XMLWebServices/TNM_Elevation_Service.asmx/getAllElevations?"
service_base_url = "http://gisdata.usgs.gov/XMLWebServices/TNM_Elevation_Service.asmx/getElevation?"


def getNEDElevation(lon,lat,units):
    query_string = "X_Value=%s&Y_Value=%s&Elevation_Units=%s&Source_Layer=NED.CONUS_NED_13W&Elevation_Only=true" % (lon,lat,units)
    response = urllib.urlopen(service_base_url + query_string).read()
    soup = BeautifulStoneSoup(response)
    return float(soup.string.contents[0])

def getNEDElevations(coords,units):
    elevs = []
    for coord in coords:
        elevs.append(getNEDElevation(coord[0],coord[1],units))
    return elevs    

def vectorProfile(shp):
    # takes the first line in the shpfile
    ds = ogr.Open(shp)
    lyr = ds.GetLayer(0)
    feat = lyr.GetFeature(0)
    geom = feat.GetGeometryRef()
    # a horrible, horrible lazy hack
    wkt = geom.ExportToWkt()
    wkt = wkt.replace("LINESTRING (","")
    wkt = wkt.replace(")","")
    wkt = wkt.replace(",","|")
    wkt = wkt.replace(" ",",")
    coords = [x.split(",") for x in wkt.split("|")]
    return getNEDElevations(coords,"ft")

if __name__ == "__main__":
    print getNEDElevations([(-113,34),(-113.1,34.05)],"ft")
    #a = vectorProfile("/home/perry/Desktop/test_track/test_track.shp")
