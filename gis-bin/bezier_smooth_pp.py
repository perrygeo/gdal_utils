#!/usr/bin/env python
import sys
import pylab
import ogr
import pp
from shapely.geometry import asLineString
from shapely.wkb import loads
#from numpy import array, asarray
import numpy

def usage():
    print
    print 'bezier_smooth.py ncpus'
    print '  ncpus = numper of worker processes to start (ideally equal to available cpu cores) '
    print 'Author: Matthew T. Perry Sept. 12 2007'
    print 
    sys.exit(1)
    
def getPointOnCubicBezier(pts,t):
    # pts[0] and pts[3] are the begin and end points
    # 1 and 2 are the "control points"
    
    x = ((1-t)**3)*pts[0][0] + 3*t*(1-t)*(1-t)*pts[1][0] + \
        3*t*t*(1-t)*pts[2][0] + (t**3)*pts[3][0]
    
    y = ((1-t)**3)*pts[0][1] + 3*t*(1-t)*(1-t)*pts[1][1] + \
        3*t*t*(1-t)*pts[2][1] + (t**3)*pts[3][1]

    return (x,y)

def computeBezier( cp, numpoints, beztype):
    dt = 1. / float(numpoints - 1)
    curve = []
    for i in range(numpoints):
        curve.append( getPointOnCubicBezier( cp, i*dt ) )

    curveArray = numpy.asarray(curve)
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
            cp1 = ( (1-t)*curve[num_bezpts-2][0] + t*p1[0] , (1-t)*curve[num_bezpts-2][1] + t*p1[1] )
        cp2 = ( (1-t)*p3[0] + t*p2[0] , (1-t)*p3[1] + t*p2[1] )
            
        cp = numpy.array( [p1, cp1, cp2, p2] )
        curve = computeBezier( cp , num_bezpts, type )
        for c in curve.tolist():
            smooth_line_list.append( c )

    smooth_line_list.append( (line[numpoints-2][0],line[numpoints-2][1]) )
    smooth_line_list.append( (line[numpoints-1][0],line[numpoints-1][1]) )
    smooth_line = numpy.asarray(smooth_line_list)

    return smooth_line

if __name__ == "__main__":
    
    num_bezpts = 8 # insert x vertcies along a bezier curve between each pair of verticies
    beztype = "cubic" # use a cubic bezier curve
    t = 1.2 # smoothing factor; must be > 1, usually ~ 1.2
    #infile = "/home/perry/Desktop/bezier_smooth/line1.shp"
    infile = "/home/perry/data/north_america_atlas/rail_l.shp"
    
    ds = ogr.Open(infile)
    lyr = ds.GetLayer(0)

    # Load up all the lines from the shapefile into a list of numpy arrays     
    lines = []
    for i in range(lyr.GetFeatureCount()):
        feat = lyr.GetFeature(i)
        geom = loads(feat.GetGeometryRef().ExportToWkb())
        lines.append(numpy.asarray(geom))
    print "Shapefile contains %d lines" % len(lines)
    
    # Start up parallel job servers
    ppservers = ()
    if len(sys.argv) > 1:
        ncpus = int(sys.argv[1])
        # Creates jobserver with ncpus workers
        job_server = pp.Server(ncpus, ppservers=ppservers)
    else:
        # Creates jobserver with automatically detected number of workers
        job_server = pp.Server(ppservers=ppservers)
    print "Starting pp with", job_server.get_ncpus(), "workers"

    # call the function farming out each line array to a parallel job
    smooth_lines = []
    jobs = [(line, job_server.submit(calcBezierFromLine, (line, num_bezpts, beztype, t), \
                                    (computeBezier, getPointOnCubicBezier), ("numpy",) )) \
             for line in lines]
    for input, job in jobs:
        smooth_lines.append( job() )
        
    # The standard non-parallized function call
    # smooth_line = calcBezierFromLine( line, num_bezpts, beztype, t)

    #for i in range(len(smooth_lines)):
    #    print "Original line: %d verticies, Bezier curve smoothed line: %d verticies" % \
    #          (lines[i].size, smooth_lines[i].size)

    print "Completed %d new lines with %d additional verticies for each line segment along a cubic bezier curve" % (len(smooth_lines), num_bezpts) 
