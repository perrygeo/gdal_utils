from osgeo import ogr
import math

INPUT = "C:\\temp\\lots\\lots.shp"
OUTPUT = "C:\\temp\\lots\\samplelocs1.shp"
INTERVAL = 30
ATTRIBMAP = {"lotid": "Parcel",
             "depth": "Depth"}

def makeLine(pta, ptb):
    line = (pta[0],pta[1],ptb[0],ptb[1])
    hyp = math.sqrt( math.pow((pta[0]-ptb[0]),2) + math.pow((pta[1]-ptb[1]),2) )
    return line, hyp

def calcNumPts(line, dist, interval):
    segs = float(dist) / float(interval)
    if segs < 1:
        segments = 1
    else:
        segments = int(segs)
    return segments

def createPoints(line,dist,numpts):
    xdif = line[0]-line[2]
    ydif = line[1]-line[3]
    points = []
    x = line[0]
    y = line[1]
    for i in range(numpts):
        x = x-(xdif/(numpts+1))
        y = y-(ydif/(numpts+1))
        points.append((x,y))
    return points

def getDirection(line):
    xdif = line[0]-line[2]
    ydif = line[1]-line[3]
    # assumes polygon in clockwise!!!
    if math.fabs(xdif) > math.fabs(ydif):
        # north or south side?
        if xdif < 1:
            return "N"
        else:
            return "S"
    else:
        # east or west side?
        if ydif < 1:
            return "W"
        else:
            return "E"

def createLotSamples(inshp, output, interval, attribmap):
    #outfh = open(output,"w")
    #outfh.write("x,y,id\n")

    ds = ogr.Open(inshp)
    lyr = ds.GetLayer(0)

    driver = ogr.GetDriverByName('ESRI Shapefile')
    outds = driver.CreateDataSource(output)
    outlayer = outds.CreateLayer("samplelocs",lyr.GetSpatialRef(),ogr.wkbPoint)
    if outlayer is None:
        raise
    fd = ogr.FieldDefn("sampleid", ogr.OFTString)
    fd.SetWidth(20)
    outlayer.CreateField(fd)
    fd = ogr.FieldDefn("depth", ogr.OFTReal)
    fd.SetWidth(10)
    fd.SetPrecision(4)
    outlayer.CreateField(fd)
    
    lyr.ResetReading()
    ftr = lyr.GetNextFeature()
    while ftr is not None:
        lotid = ftr.GetField( attribmap['lotid'] )
        depth = ftr.GetField( attribmap['depth'] )
        geom = ftr.GetGeometryRef()
        # Get the outer linearring, that's all we care about
        poly = geom.GetGeometryRef(0)
        numpoints = poly.GetPointCount()
        allsamples = []
        dircount = {'W':0,'E':0,'N':0,'S':0}
        for i in range(numpoints-1):
            line, dist = makeLine(poly.GetPoint(i), poly.GetPoint(i+1))
            numpts = calcNumPts(line, dist, interval)
            samples = createPoints(line,dist,numpts)
            direction = getDirection(line)
            for j in range(len(samples)):
                allsamples.append((samples[j][0],samples[j][1],lotid,direction,depth))
                dircount[direction] += 1

        currentdircount = {'W':0,'E':0,'N':0,'S':0}
        
        for s in allsamples:
            currentdircount[s[3]] += 1
            outfeat = ogr.Feature(feature_def=outlayer.GetLayerDefn())
            outfeat.SetGeometry( ogr.CreateGeometryFromWkt("POINT(%f %f)" % (s[0],s[1])) )
            outfeat.SetField( 0, "SW-%s-%s%s-%s" % (s[2], currentdircount[s[3]] , s[3], s[4]) )
            outfeat.SetField( 1, s[4])
            outlayer.CreateFeature(outfeat)
            outfeat.Destroy()
            #outfh.write( ",".join([str(s[0]), str(s[1]), "SW-%s-%s%s-%s" % (s[2], currentdircount[s[3]] , s[3], s[4])]) )
            #outfh.write("\n")

        centroid = geom.Centroid().GetPoint(0)
        outfeat = ogr.Feature(feature_def=outlayer.GetLayerDefn())
        outfeat.SetGeometry( ogr.CreateGeometryFromWkt("POINT(%f %f)" % (centroid[0],centroid[1])) )
        outfeat.SetField( 0, "CB-%s-1-%s" % (s[2], s[4]) )
        outfeat.SetField( 1, s[4])
        outlayer.CreateFeature(outfeat)
        outfeat.Destroy()
        
        #outfh.write( ",".join([str(centroid[0]), str(centroid[1]), "CB-%s-1-%s" % (s[2], s[4])]) )       
        #outfh.write("\n")

        ftr.Destroy()
        ftr = lyr.GetNextFeature()

    outds.Destroy()
    #outfh.close()

if __name__ == "__main__":
    createLotSamples(INPUT, OUTPUT, INTERVAL, ATTRIBMAP)
