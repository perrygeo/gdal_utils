# boxes.py
# Author: Matthew Perry
# Date: 12/19/2007
# Abstract: 
"""
Generate a polygon shapefile or feature class with several rectangles from a table that includes these fields:

X - easting of midpoint of rectangle
TopY - northing of "top" of rectangle
BottomY - northing of "bottom" of rectangle
Attribute 1 (string)
Attribute 2 (double precision)
Attribute 3 (string)

-rectangles are constant width
-rectangles will overlap; topology is not an issue.
"""
try:
   from osgeo import ogr
except ImportError:
   import ogr
import ogr
import sys
import os


def usage():
    usage = """
--------------------------------------------------------------
boxes.py <input csv file*> <constant width> <output shapefile>
csv file must be formatted like the following example... 
    
X,ytop,ybot,att1,att2,att3
10,30,20,test,21.22,a
15,29,25,test2,22.33,b

Avoid commas in the field values,
Avoid spaces in the column names, and 
Make sure the first 3 columns are numeric.
--------------------------------------------------------------
"""
    print usage
    sys.exit()

def make_boxes(infile, width, outshp):
    # read the input csv file
    fh = open(infile)
    rows = fh.readlines()
    header = rows[0].strip().split(",")
    data = [x.strip().split(",") for x in rows[1:]]
    width = float(width)
    
    #Create the layer
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(outshp):
        print "Output file", outshp,"already exists."
        sys.exit(1)
    ds = driver.CreateDataSource(outshp)
    layer = ds.CreateLayer(outshp, geom_type=ogr.wkbPolygon)
    
    # Create the field definitions; either a string or a number
    for i in range(len(header)):
        try:
            # is it a number ? Check the value in the first row
            test = float(data[0][i]) 
            # it's a number ... treat as a double precision
            fd = ogr.FieldDefn(header[i], ogr.OFTReal)
            fd.SetWidth(30)
            fd.SetPrecision(11)
            layer.CreateField(fd)	
        except ValueError:  
            # not a number; treat as 255 char string        
            fd = ogr.FieldDefn(header[i], ogr.OFTString)
            fd.SetWidth(255)
            layer.CreateField(fd)	
    
    # loop through the data
    for d in data:
        # Create the feature
        f= ogr.Feature(feature_def=layer.GetLayerDefn())

        # Fill in the attribute fields
        for colnum in range(len(header)):
           f.SetField(colnum, d[colnum])

        # create a geometry
        try:
            xmid = float(d[0])
            x = xmid - (width/2)
            ytop = float(d[1])
            ybot = float(d[2])
            # bottom shouldn't be > than top but, if it is, handle gracefully assuming they are meant to be swapped
            if ybot > ytop:
               print "WARNING: top Y %f is less than bottom Y %f - fixed" % (ytop,ybot)
               temp = ybot
               ybot = ytop
               ytop = temp
            if ybot == ytop:
               print "WARNING: top Y and bottom Y are equal - offsetting by 0.001" 
               ybot = ybot - 0.001
	        # Create the point feature
            wkt = 'POLYGON((%f %f, %f %f, %f %f, %f %f, %f %f))' % \
                  (x, ytop, x+width, ytop, x+width, ybot, x, ybot, x, ytop)
            g = ogr.CreateGeometryFromWkt(wkt)
            f.SetGeometryDirectly(g)
            layer.CreateFeature(f)
            layer.SyncToDisk()
        except:
            print "WARNING: The following row in the input data is not valid and will be skipped:\n     " + str(d)
            
	    f.Destroy()

    # destroying data source closes the output shp/dbf file
    ds.Destroy()         
    return
    
if __name__ == "__main__":
    try:
        infile = sys.argv[1]
        width = sys.argv[2]
        outshp = sys.argv[3]
    except:
        # you can uncomment and use hardcoded values for testing
        #infile = "C:\\Workspace\\boxes\\test.csv"
        #width=5
        #outshp = "C:\\Workspace\\boxes\\shptry1.shp"
        usage()
    
    make_boxes(infile,width,outshp)
