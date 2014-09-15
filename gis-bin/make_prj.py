#!/usr/bin/env python

import osr
import sys


try:
    source = sys.argv[1]
    dest = sys.argv[2]
    projection = ''
    for i in range(3,len(sys.argv)):
        #print sys.argv[i]
        projection += " " + sys.argv[i]
except:
    print 
    print "Usage:"
    print "generate_prj.py proj4 esri +proj=stere +lat_0=...."
    print "generate_prj.py epsg wkt 4326"
    print
    print "syntax : source_format{proj4|epsg} dest_format{esri|wkt} projection_definition"
    print
    sys.exit(1)

    
srs = osr.SpatialReference()

if source == 'proj4':
    srs.ImportFromProj4(projection)
elif source == 'epsg':
    srs.ImportFromEPSG(int(projection))

if dest == 'esri':
    srs.MorphToESRI()

prj = srs.ExportToWkt()

print prj
