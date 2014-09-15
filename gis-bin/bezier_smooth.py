#!/usr/bin/env python
#import ogr
import sys
import pylab
from osgeo import ogr
from shapely.geometry import asLineString
from shapely.wkb import loads
from numpy import array, asarray

def CloneLayer ( ds, src_layer ):
    ''' create output layer as a clone of source layer '''
    defn = src_layer.GetLayerDefn()

    dest_layer = ds.CreateLayer( 
    defn.GetName(), src_layer.GetSpatialRef(), defn.GetGeomType()  )

    for i in range( defn.GetFieldCount() ):
        src_fd = defn.GetFieldDefn( i )
        dest_fd = ogr.FieldDefn( src_fd.GetName(), src_fd.GetType() )
        dest_fd.SetWidth( src_fd.GetWidth() )
        dest_fd.SetPrecision( src_fd.GetPrecision() )
        dest_layer.CreateField( dest_fd )

    return dest_layer
    
def getPointOnCubicBezier(pts,t):
    # pts[0] and pts[3] are the begin and end points
    # 1 and 2 are the "control points"
    
    x = ((1-t)**3)*pts[0][0] + 3*t*(1-t)*(1-t)*pts[1][0] + \
        3*t*t*(1-t)*pts[2][0] + (t**3)*pts[3][0]
    
    y = ((1-t)**3)*pts[0][1] + 3*t*(1-t)*(1-t)*pts[1][1] + \
        3*t*t*(1-t)*pts[2][1] + (t**3)*pts[3][1]

    return (x,y)

def getPointOnQuadraticBezier(pts,t):
    # pts[0] and pts[3] are the begin and end points
    # 1 and 2 are the "control points"

    avg_cpx = (pts[1][0] + pts[2][0]) / 2.
    avg_cpy = (pts[1][1] + pts[2][1]) / 2.
    
    x = ((1-t)**2)*pts[0][0] + 2*t*(1-t)*avg_cpx + t*t*pts[3][0]
    y = ((1-t)**2)*pts[0][1] + 2*t*(1-t)*avg_cpy + t*t*pts[3][1]

    return (x,y)

def computeBezier( cp, numpoints, beztype):
    dt = 1. / float(numpoints - 1)
    curve = []
    for i in range(numpoints):
        if beztype == "cubic":
            curve.append( getPointOnCubicBezier( cp, i*dt ) )
        elif beztype == "quadratic":
            curve.append( getPointOnQuadraticBezier( cp, i*dt ) )
        else:
            curve.append( getPointOnCubicBezier( cp, i*dt ) )

    curveArray = asarray(curve)
    return curveArray

def calcBezierFromLine( line, num_bezpts, beztype, t):
    #start the smooth line
    smooth_line_list = [ (line[0][0],line[0][1])]

    numpoints = line.shape[0]
    curve = None
    for i in range(1, numpoints-3):
        p0 = line[i-1]
        p1 = line[i]
        p2 = line[i+1]
        p3 = line[i+2]

        if curve is None:
            cp1 = ( (1-t)*p0[0] + t*p1[0] , (1-t)*p0[1] + t*p1[1] )
        else:
            cp1 = ( (1-t)*curve[num_bezpts-2][0] + t*p1[0] ,
                    (1-t)*curve[num_bezpts-2][1] + t*p1[1] )
        cp2 = ( (1-t)*p3[0] + t*p2[0] , (1-t)*p3[1] + t*p2[1] )
            
        cp = array( [p1, cp1, cp2, p2] )
        curve = computeBezier( cp , num_bezpts, type )
        for c in curve.tolist():
            smooth_line_list.append( c )

    smooth_line_list.append( (line[numpoints-2][0],line[numpoints-2][1]) )
    smooth_line_list.append( (line[numpoints-1][0],line[numpoints-1][1]) )
    smooth_line = asarray(smooth_line_list)

    return smooth_line


if __name__ == "__main__":
    num_bezpts = 256
    beztype = "cubic"
    t = 1.3 # must be > 1, usually ~ 1.2
    show_only = False # False will create shp, True will show with pylab
    if len(sys.argv)>1 and sys.argv[1]=="show":
        show_only = True 
    outfile = "/home/perry/active/bezier_smooth/smooth"
    infile = "/home/perry/active/bezier_smooth/line1.shp"
    
    ds = ogr.Open(infile)
    lyr = ds.GetLayer(0)

    if show_only is False:
        # Create output dataset/layer
        driver = ogr.GetDriverByName('ESRI Shapefile')
        outds = driver.CreateDataSource(outfile)
        outlayer = CloneLayer( outds, lyr )

    for i in range(lyr.GetFeatureCount()):
        feat = lyr.GetFeature(i)
        geom = loads(feat.GetGeometryRef().ExportToWkb())
        line = asarray(geom)

        smooth_line = calcBezierFromLine( line, num_bezpts, beztype, t)

        if show_only is True:
            pylab.plot( line[:,0] - 2., line[:,1] )
            pylab.plot( smooth_line[:,0], smooth_line[:,1] )
        else:
            sl = asLineString( smooth_line )
              
            # Loop thru fields and clone attributes
            field_count = lyr.GetLayerDefn().GetFieldCount()
            outfeature = ogr.Feature(feature_def=outlayer.GetLayerDefn())
            for i in range(field_count):
                 outfeature.SetField( i, feat.GetField(i) )
 
            new_geom = ogr.CreateGeometryFromWkt(sl.wkt)
            outfeature.SetGeometry( new_geom )
            outlayer.CreateFeature( outfeature )
        
    if show_only is True:
        pylab.show()
    else:
        ds.Destroy()
        outds.Destroy()
