import ogr
import pylab
from numpy import asarray, zeros
from shapely.wkb import loads
import pylab
    
def getPointsList(ogrlayer):
    points = []
    while 1:
        feature = ogrlayer.GetNextFeature()
        if not feature:
            break

        geom = loads(feature.GetGeometryRef().ExportToWkb())
        #fid = feature.GetFID()
        points.append(geom)
        
    return points

def getDistanceMatrix(point_list):
    dist_matrix = zeros( (len(point_list),len(point_list)) , float)
    fcnt = 0
    for f in points:
        tcnt = 0
        for t in points:
            dist_matrix[fcnt,tcnt] = f.distance(t)
            tcnt += 1
        fcnt += 1
    return dist_matrix

def getDistancesToNearest(point_list):
    nearest = []
    for f in points:
        dists = zeros( len(point_list), float )
        tcnt = 0
        for t in points:
            dists[tcnt] = f.distance(t)
            tcnt += 1
        nearest.append( dists[dists>0].min() )
        
    return nearest

def plotGFunction(dists):
    # !! This whole function should probably be using arrays instead of lists
    # Sort the distances and get some basic stats
    dists.sort()
    maxdist = max(dists)
    n = len(dists)

    # Find the cumulative frequency (ie frequency of non-exceedance)
    cumfreq = []
    for d in dists:
        cumfreq.append( float(len( [x for x in dists if x <= d] )) / float(n) )

    # plot
    pylab.grid()
    pylab.plot([0]+dists, [0]+cumfreq )
    pylab.show()
    return 
 
if __name__ == "__main__":

    source = ogr.Open("/home/perry/Desktop/G Function/cluster.shp")
    #source = ogr.Open("/home/perry/data/world_cities/cities.shp")
    #source = ogr.Open("/home/perry/Desktop/G Function/even.shp")
    layer = source.GetLayer()
    points = getPointsList(layer)
    n = getDistancesToNearest(points)
    plotGFunction(n)

##  x = getDistanceMatrix(points)


