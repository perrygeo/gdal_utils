#!/usr/bin/env python
# txt2shp.py
# Matthew Perry
# Dec 3 2005

import sys

def usage():
	print """
    Converts a delimited text file with x/y coords into a point shapefile
    and retains all other data columns in the dbf

    Usage:
    txt2shp.py input=input.txt output=output.shp [wb=X] [d=X]

      wb -> width buffer : make column wider than largest data value (default 2)
      d -> delimiter     : string delimiting each column (default is , )

    There are a few strict formatting requirements for the input data:
      - columns must be delimited by a character not appearing in the content
      - rows are delimited by line breaks
      - input file must include two and *only* two header rows:
        1st row : column names (up to 10 charachters wide)
        2nd row : column types (string, integer, real, x or y)
      - Must have one numeric column of type 'x" and one of type 'y' 
          to create a point

    Example input file:

      lat,long,elevation,name
      x,y,real,string
      -122.45,42.865,580,point A
      -122.55,43.015,280,point B
	"""
	sys.exit(1)

# Defaults
delimiter = ","
widthBuffer = 2
override = 1
output = None
inputFile = None

try:
   for i in range(len(sys.argv)):
      p = sys.argv[i].split('=')

      if p[0] == 'input':
         inputFile = str(p[1])
      if p[0] == 'output':
         output = str(p[1])
      if p[0] == 'wb':
         widthBuffer = str(p[1])
      if p[0] == 'd':
         delimiter = str(p[1])
except:
	usage()

if not inputFile or not output:
	usage()

import os
if not os.path.exists(inputFile):
	print "Input File",inputFile,"doesn't exist"
	sys.exit()

import ogr
myFile = open(inputFile, 'r')

# open the input text file
# confirm the header rows
# count num of columns
# read through data rows and determine column max
maxWidth = []
precision = []
count = 0
line = myFile.readline()
while line:
	count = count + 1

	cleanline = line.replace('\n','')
	cols = cleanline.split(delimiter)
	if count==1:
		colNames=cols
		for i in range(len(colNames)):
			maxWidth.append(0)
			precision.append(0)
	elif count==2:
		colTypes=cols
		for i in range(len(colTypes)):
			colType = str(colTypes[i].strip())
			if colType == 'string':
				colTypes[i] = ogr.OFTString
			elif colType == 'integer':
				colTypes[i] = ogr.OFTInteger
			elif colType == 'real':
				colTypes[i] = ogr.OFTReal
			elif colType == 'x':
				colTypes[i] = ogr.OFTReal
				xCol = i
			elif colType == 'y':
				colTypes[i] = ogr.OFTReal
				yCol = i
			else:
				print "Column",i,"has an invalid column type", colType
				usage()
	else:
		#Loop through cols and set max
                if len(cols) < len(colNames):
                    line = myFile.readline()
                    print "Skipped line", count
                    continue

		for i in range(len(colNames)):
			# Find max column width
			if len(cols[i]) > maxWidth[i]:
				maxWidth[i] = len(cols[i])
			# Find max decimal places
			if colTypes[i] == ogr.OFTReal:
				full = str(cols[i])
				parts = full.split('.')
                                if len(parts) == 2:
					decPlaces = len(parts[1])
					if decPlaces > precision[i]:
					    precision[i] = decPlaces
				
	line = myFile.readline()

myFile.close()

# Create the Shapefile
# Set input/output driver
driver = ogr.GetDriverByName('ESRI Shapefile')

#Create the layer
if os.path.exists(output):
	if override == 1:
            driver.DeleteDataSource(output)
        else:
            print
            print "Output file", output,"already exists."
            print
            sys.exit(1)

ds = driver.CreateDataSource(output)
layer = ds.CreateLayer(output, geom_type=ogr.wkbPoint)

# Create fields
for j in range(len(colNames)):
	fd = ogr.FieldDefn(colNames[j].strip(), colTypes[j])
	fd.SetWidth(maxWidth[j] + widthBuffer)
	fd.SetPrecision(precision[j]+1)
	layer.CreateField(fd)	
	

# Second pass.. this time take the data and create our shapefile
myFile = open(inputFile, 'r')

# Skip the first two rows
line = myFile.readline()
line = myFile.readline()

line = myFile.readline()
while line:
	cleanline = line.replace('\n','')
	cols = cleanline.split(delimiter)

	# Create the feature
	f= ogr.Feature(feature_def=layer.GetLayerDefn())

	# Fill in the attribute fields
	for colNum in range(len(cols)):
		f.SetField(colNum, cols[colNum])

	#If there is a lat/long, use it to create a geometry
	if cols[xCol] and cols[yCol]:
	    x = float(cols[xCol])
	    y = float(cols[yCol])
	    # Create the point feature
 	    wkt = 'POINT(%f %f)' % (x, y)
	    g = ogr.CreateGeometryFromWkt(wkt)

	    f.SetGeometryDirectly(g)
	    layer.CreateFeature(f)

	f.Destroy()
	line = myFile.readline()

# destroying data source closes the output shp/dbf file
ds.Destroy()

if os.path.exists(output):
        print
	print "Output file", output, "created successfully."
        print









