#!/usr/bin/env python
"""
  xyz2postgis.py
  takes an xyz file and creates a table with geometry and a single z column
"""

import os
import sys
import ogr

#xyz = '/home/perry/data/pop/pop2001.xyz'
xyz = '/home/perry/data/pop/test.xyz'
output_table = 'test'

# Define the continents, extents and projections

# Create the table
ds = ogr.Open('PG:host=localhost dbname=perry user=perry') 
layer = ds.CreateLayer(output_table, geom_type=ogr.wkbPoint)

# Create z column
fd = ogr.FieldDefn('z', ogr.OFTInteger)
#fd.SetWidth(8)
layer.CreateField(fd)	

# Parse file and loop through rows
fh = open(xyz,'r')
line = fh.readline()
while line:
    cleanline = line.replace('\n','')
    cols = cleanline.split(' ')
    if len(cols) != 3:
        line = fh.readline()
        continue 
    lon = cols[0]     
    lat = cols[1]
    z   = float(cols[2])

    if z >= 0:
        f= ogr.Feature(feature_def=layer.GetLayerDefn())
        wkt = 'POINT(%f %f)' % (float(lon), float(lat))
        p = ogr.CreateGeometryFromWkt(wkt)
        #p.AssignSpatialReference(latlong)
        #proj = '+proj=ortho +lon_0=%f +lat_0=%f' % (x,y)
        #ortho.ImportFromProj4(proj)
        #p.TransformTo(ortho)
        #b = p.Buffer(640000)
        #b.AssignSpatialReference(ortho)
        #b.TransformTo(latlong)
        f.SetGeometryDirectly(p)
        f.SetField(0,int(z))
        layer.CreateFeature(f)
        f.Destroy()
       
        # Loop through continents
        #  Reproject
        #  Clip
        #  Create geom and fill in column

    line = fh.readline()

ds.Destroy()
