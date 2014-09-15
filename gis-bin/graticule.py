# craticule_hack.py
# Credits to Sean Gillies
# http://zcologia.com/news/16
#
import math
import ogr

# Create an ESRI shapefile of parallels and meridians for a MapServer
# world map.

filename = 'graticule.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
driver.DeleteDataSource(filename)
ds = driver.CreateDataSource(filename)
layer = ds.CreateLayer('graticule', geom_type=ogr.wkbLineString)

#Next, define several attribute fields. 
#A 'TYPE' field will let me classify and render differently the parallels and meridians if I so choose.
# 'VALUE' and 'ABS_VALUE' fields will be useful for labeling the parallels and meridians:

# Create an integer field for classification
# 0: parallel
# 1: meridian
fd = ogr.FieldDefn('TYPE', ogr.OFTInteger)
fd.SetWidth(1)
fd.SetPrecision(0)
layer.CreateField(fd)

# Create two fields for labeling
fd = ogr.FieldDefn('VALUE', ogr.OFTInteger)
fd.SetWidth(4)
fd.SetPrecision(0)
layer.CreateField(fd)

fd = ogr.FieldDefn('ABS_VALUE', ogr.OFTInteger)
fd.SetWidth(4)
fd.SetPrecision(0)
layer.CreateField(fd)

#Next, create parallels and insert them into the layer:

# First, the parallels at 10 degree intervals, with one degree resolution
for j in range(1,18):
    y = 10*float(j-9)
    for i in range(0, 360):
        line = ogr.Geometry(type=ogr.wkbLineString)
        
        # hack: MapServer has trouble within .1 decimal degrees of the
        # dateline
        if i == 0:
            x1 = -179.9
            x2 = -179.0
        elif i == 359:
            x1 = 179.0
            x2 = 179.9
        else:
            x1 = float(i-180)
            x2 = x1 + 1.0
            
        line.AddPoint(x1, y)
        line.AddPoint(x2, y)
    
        f = ogr.Feature(feature_def=layer.GetLayerDefn())
        f.SetField(0, 0)
        f.SetField(1, y)
        f.SetField(2, math.fabs(y))
        f.SetGeometryDirectly(line)
        layer.CreateFeature(f)
        f.Destroy()

#And now the meridians:

# Next, the meridians at 10 degree intervals and one degree resolution

for i in range(0, 37):
    x = 10*float(i-18)

    # hack: MapServer has trouble within .1 decimal degrees of the
    # dateline
    if i == 0:
        x = -179.9
    if i == 36:
        x = 179.9

    for j in range(10, 170):
        line = ogr.Geometry(type=ogr.wkbLineString)
        y1 = float(j - 90)
        y2 = y1 + 1.0
        
        line.AddPoint(x, y1)
        line.AddPoint(x, y2)
    
        f = ogr.Feature(feature_def=layer.GetLayerDefn())
        f.SetField(0, 1)
        f.SetField(1, x)
        f.SetField(2, math.fabs(x))
        f.SetGeometryDirectly(line)
        layer.CreateFeature(f)
        f.Destroy()

# destroying data source closes the output file
ds.Destroy()

#Because the Python Cartographic Library doesn't yet support non-EPSG coordinate systems 
#(coming soon), I'm going to use MapServer's scripting module to draw the graticules:

import mapscript

mo = mapscript.mapObj()
mo.setFontSet('/home/sean/projects/ms_44/mapserver/tests/fonts.txt')
mo.selectOutputFormat('image/png')

layer = mapscript.layerObj()
layer.status = mapscript.MS_DEFAULT
layer.data = 'graticule.shp'
layer.setProjection('+init=epsg:4326')
layer.type = mapscript.MS_LAYER_LINE
layer.labelitem = 'VALUE'
layer.classitem = 'TYPE'
li = mo.insertLayer(layer)
layer = mo.getLayer(li)

# render parallels and meridians in same style
style = mapscript.styleObj()
style.color.setHex('#808080')

co = mapscript.classObj()
co.label.type = mapscript.MS_TRUETYPE
co.label.font = 'Vera'
co.label.size = 6
co.label.position = mapscript.MS_AUTO
co.label.mindistance = 200

co.insertStyle(style)
co.setExpression('([TYPE] EQ 0)')
co.label.color.setRGB(0, 255, 0)
layer.insertClass(co)

style.color.setHex('#0000FF')
co.insertStyle(style)
co.setExpression('([TYPE] EQ 1)')
co.label.color.setRGB(255, 0, 0)
layer.insertClass(co)

#Next, draw the graticule using a Mollweide projection:

# Mollweide Projection
mo.setSize(600, 300)
mo.setProjection('+proj=moll +lon_0=0.0')
mo.setExtent(-18100000, -9050000, 18100000, 9050000)
im = mo.draw()
im.save('graticule-moll.png')

#And finally, an Orthographic projection:

mo.setSize(400, 400)
mo.setProjection('+proj=ortho +lon_0=0.0 +lat_0=40.0')
mo.setExtent(-6400000,-6400000,6400000,6400000)
im = mo.draw()
im.save('graticule-ortho.png')
