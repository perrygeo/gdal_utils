#!/usr/bin/env python
"""
  GPX Report
  Given a track gpx file, creates a full report of the track

  Currently just outputs an elevation profile
  
  TODO:
   calculate slope and speed profiles
   min,max,avg elevations, speeds, slopes
   total elevation gain
   distance
   trailhead latlong
   directions to trailhead (reverse geocode trailhead then get directions)
   map of track (shdrelief, rivers, roads, placenames, contours, trailhead, aerial)
   output all to pdf 
  
  Matthew Perry
  Apache 2.0 License
"""
import sys
import gdal
from great_circle import greatCircle
#from rasterQuery import getRasterValue
from elevationClient import getNEDElevation
try:
    from xml.etree.ElementTree import Element, ElementTree
except ImportError:
    from elementtree.ElementTree import ElementTree

def parseTrkpnts(gpx):
    namespace = '{http://www.topografix.com/GPX/1/0}'

    root = ElementTree(file=gpx)
    trkpnts = []

    for element in root.getiterator():
        if element.tag == namespace + 'trkpt' and element.keys():
            for name, value in element.items():
                if name == 'lat': lat = value
                if name == 'lon': lon = value
            for child in element.getchildren():
                if child.tag == namespace + 'ele': ele = child.text
                if child.tag == namespace + 'time': time = child.text

            trkpnts.append( {'ele': float(ele), 'time':time, 'lat':float(lat), 'lon':float(lon)} )

    return trkpnts

def createProfile(trkpnts,raster="/home/perry/data/sbdata/sbdems/sbdems.tif",hunits="mi"):
    elevs = []
    dists = []
    pnt1_lat = None 
    pnt1_lon = None
    pnt2_lat = None
    pnt2_lon = None
    for i in trkpnts:
        if pnt2_lat is None and pnt2_lon is None:
            pnt2_lat = i['lat']
            pnt2_lon = i['lon']
            cumdist = 0
        else:
            pnt1_lat = pnt2_lat
            pnt1_lon = pnt2_lon
            pnt2_lat = i['lat']
            pnt2_lon = i['lon']
            dist = greatCircle(pnt1_lon,pnt1_lat,pnt2_lon,pnt2_lat,units="mi")
            cumdist = cumdist + dist
#       elevs.append( getRasterValue(pnt2_lon,pnt2_lat,raster,window=1) )
        elevs.append( getNEDElevation(pnt2_lon,pnt2_lat,"ft") )
        dists.append(cumdist)
    profile = {'elevs':elevs, 'dists':dists}
    return profile
    
def plotProfile(profile):
    import pylab 
    pylab.plot(profile['dists'],profile['elevs'])
    pylab.show()

if __name__ == '__main__':
    trkpnts = parseTrkpnts(sys.argv[1])
    profile = createProfile(trkpnts)
    print profile
    plotProfile(profile)
    
    
