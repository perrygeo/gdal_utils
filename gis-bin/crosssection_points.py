import math

def getPointsFromShp(shp, labelfield):
    from osgeo import ogr
    ds = ogr.Open(shp)
    if ds is None: raise
    layer = ds.GetLayer(0)
    label_index = layer.GetLayerDefn().GetFieldIndex(labelfield)
    feature = layer.GetNextFeature()
    points = {}
    while feature is not None:
        label = feature.GetFieldAsString(label_index)
        geom = feature.GetGeometryRef()
        coords = (geom.GetX(), geom.GetY())
        points[label] = coords
        feature = layer.GetNextFeature()
    return points

def calcDistance(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def getTransectsFromShp(shp, labelfield):
    from osgeo import ogr
    ds = ogr.Open(shp)
    if ds is None: raise
    layer = ds.GetLayer(0)
    label_index = layer.GetLayerDefn().GetFieldIndex(labelfield)
    feature = layer.GetNextFeature()
    transects = {}
    while feature is not None:
        label = feature.GetFieldAsString(label_index)
        geom = feature.GetGeometryRef()
        numpoints = geom.GetPointCount()
        points = []
        cum_dist = 0.0
        for i in range(0, numpoints):
            current_point = geom.GetPoint(i)
            if i == 0:
                point = (current_point[0],current_point[1],0.0)
            else:
                cum_dist += calcDistance( geom.GetPoint(i-1), current_point)
                point = (current_point[0],current_point[1], cum_dist)
                
            points.append( point )
        transects[label] = points
        feature = layer.GetNextFeature()
    return transects

def calcAngle(A, C, B):
    a = calcDistance(C, B)
    b = calcDistance(A, C)
    c = calcDistance(A, B)
    alpha = math.acos( (b**2 + c**2 - a**2)/ (2*b*c) )
    return alpha

    
def calcPointTransects(points, transects, thresholdDistance, raster_file=None):
    results = {}
    if raster_file is not None:
        from osgeo import gdal
        ds = gdal.Open(raster_file)
        gt = ds.GetGeoTransform()
        cellsize = (gt[1]-gt[5])/2
        band = ds.GetRasterBand(1)
        
    for t in transects.keys():
        trans = {}
        if raster_file is not None: rastvalues = {}
        distOffset = 0.0
        for s in range(1,len(transects[t])):
            for p in points.keys():
                distOffset = transects[t][s-1][2]
                alpha = calcAngle(transects[t][s-1], transects[t][s], points[p])
                distOriginToPoint = calcDistance(transects[t][s-1],points[p])
                lengthTransectSeg = calcDistance(transects[t][s-1], transects[t][s])
                distFromLine = distOriginToPoint * math.sin(alpha)
                if distFromLine <= thresholdDistance:
                    distAlongSegment = distOriginToPoint * math.cos(alpha)
                    if distAlongSegment >= 0 and distAlongSegment <= lengthTransectSeg:
                        distAlongLine = distOffset + distAlongSegment
                        trans[p] = distAlongLine
                        if raster_file is not None:
                            rastvalues[p] = getRasterValue(points[p][0],points[p][1],band,gt)

        # Sort the transect points
        # and break into two lists (can be zipped back together if needed)               
        hist = [ (v, k) for k, v in trans.iteritems() ]
        hist.sort()
        transectPoints = []
        transectDists = []
        if raster_file is not None: transectRastValues = []
        
        for h in hist:
            transectDists.append(h[0])
            transectPoints.append(h[1])
            if raster_file is not None:
                transectRastValues.append( rastvalues[h[1]] )
            
        if raster_file is not None:
            results[t] = (transectDists, transectRastValues, transectPoints)
        else:
            results[t] = (transectDists, transectPoints)
        #print zip(transectPoints, transectDists)
    return results

def getXYfromM( pts, M):
    for i in range(len(pts)):
        if pts[i][2] > M:
            seg = (pts[i-1], pts[i])
            offset = pts[i-1][2]
            break
    if not seg: raise
    alpha = calcAngle(seg[0], seg[1], (seg[0][0],0))      
    opp = (M - offset) * math.sin(alpha)
    adj = (M - offset) * math.cos(alpha)
    
    if seg[0][0] < seg[1][0]:
        # trends east  
        newpt = (seg[0][0] + opp, seg[0][1] - adj)
    else:
        # trends west
        newpt = (seg[0][0] - opp, seg[0][1] - adj)
    return newpt

def getRasterValue(x,y,band,gt):
    xoff = int((x - gt[0]) / gt[1])  
    yoff = int((y - gt[3]) / gt[5]) 
    try:
        a = band.ReadAsArray( xoff, yoff, 1, 1)
        return a[0][0]        
    except:
        print "Coordinates (%s, %s) out of range" % (x,y)
        return None

    
def calcRasterTransects(transects, raster_file, output_points=None):
    from osgeo import gdal
    from numpy import arange
    ds = gdal.Open(raster_file)
    gt = ds.GetGeoTransform()
    cellsize = (gt[1]-gt[5])/2
    band = ds.GetRasterBand(1)
    if output_points:
        ofh = open(output_points,'w')
        ofh.write("x,y,id,transect\n")
    xsecs = {}
    for t in transects.keys():
        xsecPoints = []
        xsecDists = []
        xsecRastValues = []
        numpoints = len(transects[t])
        maxlen = transects[t][numpoints-1][2]
        for i in arange(0,maxlen,cellsize*2):
            coords = getXYfromM(transects[t],i)
            if output_points:
                ofh.write(",".join(str(j) for j in coords))
                ofh.write("," + str(i))
                ofh.write(","+t)
                ofh.write("\n")
            rastval = getRasterValue(coords[0],coords[1],band,gt)
            xsecDists.append(i)
            xsecRastValues.append(rastval)
        xsecs[t] = (xsecDists, xsecRastValues)
    if output_points: ofh.close()
    return xsecs

def zipToCSVs(results, header, outfile_prefix):
    for r in results.keys():
        if len(header) == 2:
            zipped = zip(results[r][0], results[r][1])
        elif len(header) == 3:
            zipped = zip(results[r][0], results[r][1], results[r][2])
        outfile = outfile_prefix + r + ".csv"
        ofh = open(outfile, 'w')
        ofh.write(",".join(header))
        ofh.write("\n")
        for z in zipped:
            ofh.write(",".join(str(x) for x in z))
            ofh.write("\n")
        ofh.close()

def makeRasterChart(results, point_results=None, basename=None, type="svg",
                    labels = ("Cross-section of Transect ","Distance","Elevation") ):
    import pylab as p

    for t in results.keys():
        p.figure(figsize=(17,8.5))
        p.plot(results[t][0], results[t][1])
        if point_results and len(point_results[t][0])>1:
            p.scatter(point_results[t][0], point_results[t][1])
            for z in zip(point_results[t][0],point_results[t][1],point_results[t][2]):
                p.annotate("   " + z[2],(z[0],z[1]),  ha='center', va='bottom', rotation="vertical", size=8)
        p.xlabel(labels[1])
        p.ylabel(labels[2])
        p.title(labels[0]+t)
        p.xlim(0,max(results[t][0]))
        p.grid(True)
        if basename:
            p.savefig(basename + t + "." + type)
            p.close()
        else:
            p.show()
  

        
if __name__ == "__main__":
    #points_shp = "P:\\GIS\\HX0130\\Shapefiles\\all_sample_locations.shp"
    points_shp = "P:\\GIS\\HX0130\\Shapefiles\\soilgas_bubbleplots\\SOILGAS_SAMPLES.shp"
    transects_shp = "P:\\GIS\\SB0324\\Shapefiles\\transect_test\\transects.shp"
    raster_file = "P:\\GIS\\HX0130\\Images\\dem\\\casdem1\\hdr.adf"
    thresholdDistance = 175.
    
    points = getPointsFromShp(points_shp, "LOCATION")
    transects = getTransectsFromShp(transects_shp, "transect")

    point_results = calcPointTransects(points, transects, thresholdDistance, raster_file)    
    raster_results = calcRasterTransects(transects, raster_file, output_points="C:\\temp\\cross\\transect_points.csv")

    zipToCSVs(point_results, ["dist","elev","pointid"], "C:\\temp\\cross\\points_")
    zipToCSVs(raster_results, ["dist","elev"], "C:\\temp\\cross\\profile_")

    makeRasterChart(raster_results, point_results, "C:\\temp\\cross\\chart_", "png")
    
            

    
    
