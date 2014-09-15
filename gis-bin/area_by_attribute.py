#!/usr/bin/env python
###############################################################################
# area_by_attribute.py,v 0.1 2005/08/23 
# Purpose:  Calculate total area by each unique attribute value for a polygon shapefile
# Author:   Matt Perry, perrygeo@gmail.com
# TBD: error checking (make sure field exists, geomtype is polygon)
#      make it accept command line arguments
#      accept units as input variable and reproject geometries before GetArea() 
#      output results to a file
###############################################################################
import ogr
#import string
#import sys

#############################
# Input variables

#attribute = "OC2"
attribute = "PTYPE"
#infile = "/home/perrygeo/data/ca_land_ownership/govtowna.shp"
infile = "/home/perrygeo/Desktop/geologic_map_ca/ArcInfo/ca_geol_4326.shp"
#layername= "govtowna"
layername= "ca_geol_4326"

# A dictionary to hold the cumulative area per each attribute
table = {}

totalArea = 0

#############################
#  Open the shapefile and retrieve the layer

shp = ogr.Open( infile, update = 0 )
layer = shp.GetLayerByName(layername)
print "Opened " + infile
print "Reading geometries and calculating area for each unique value of field \"" + attribute + "\" .... "

#############################
# Loop thru each polygon feature and calculate cumulative area 
# depending upon the attribute

feature = layer.GetNextFeature()
while feature is not None:
	area = feature.GetGeometryRef().GetArea()
	value = feature.GetField( attribute )

	if table.has_key(value):
		cumulativeArea = table.get(value) + area
		table[value] = cumulativeArea
	else:
		addarea = {value:area}
		table.update(addarea)

	totalArea = totalArea + area
 	feature.Destroy()
	feature = layer.GetNextFeature()         

##############################
# Output the results

print attribute , "Area", "Percentage"

for unique in table.keys():
        pct = round(100 * (table[unique]/totalArea),4)
	print unique, table[unique], pct
print '', "---------"
print 'TOTAL', totalArea
	
##############################
# Clean house

shp.Destroy()
