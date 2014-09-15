#!/usr/bin/python
import sys
import ogr
import os

def usage():
    print
    print 'guess_proj.py dataset approximate-longitude approximate-latitude verbose'
    print 'Notes : '
    print 'Author: Matthew T. Perry Sept. 17, 2005 '
    print 
    sys.exit(1)

def error(message):
    print
    print message
    print
    sys.exit(1)

def getArgs(args):
    dataset = None
    lon = None
    lat = None
    verbose = None 

    for i in range(1, len(sys.argv)):
	arg = sys.argv[i]

	if dataset is None:
	    dataset = arg
	elif lon is None:
	    lon = float(arg)
	elif lat is None:
	    lat = float(arg)
	elif verbose is None:
	    verbose = True 
	else:
	    usage()
     
    if (dataset is not None and lat is not None and lon is not None):
        return dataset, lon, lat, verbose
    else:
        usage()    

def getProjList(lon,lat):
    srs = []

    import epsg_projections
    for k in epsg_projections.epsg.keys():
        srs.append([epsg_projections.epsg[k], "EPSG:" + str(k)])

    # ca state plane and teale albers systems
    srs.append(["+proj=aea +lat_1=34.00 +lat_2=40.50 +lat_0=0.00 +lon_0=-120.00 +x_0=0.000 +y_0=-4000000.000 +ellps=GRS80 +units=m +datum=NAD83", "teale albers"])
    
    return srs

if __name__ == "__main__":
    dataset, lon, lat, verbose = getArgs(sys.argv);

    # Open the input dataset and get the layer
    ds = ogr.Open(dataset)
    lyr = ds.GetLayer()
     
    # Get bounds
    bbox = lyr.GetExtent()
    if (bbox[0]>=-180 and bbox[1]<=180 and bbox[2]>=-90 and bbox[3]<=90):
        print "Your dataset is probably in geographic (latlong) coordinates"
        print "There are tons of potential datums so it's up to you to find out"
        print " which one your data is in"
        sys.exit(0)
    # Get list of possible srs
    projs = getProjList(lon,lat)

    # Loop thru srs and test if the coordinates match
    for proj in projs:
        cmd = "echo '%f %f' | cs2cs -f '%s' +proj=latlong +to %s" % (lon,lat, '%.6f', proj[0])
        res = os.popen(cmd).read().split( )
        x = float(res[0])
        y = float(res[1])
        if verbose:
            print
            print proj
            print res
            print bbox

        if (x > bbox[0] and x < bbox[1] and y > bbox[2] and y < bbox[3]):
            print " ************" ,proj[1] , "matches *********"

        
