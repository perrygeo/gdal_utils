#!/usr/bin/env python
import math
import sys

pi = math.pi 

def getArgs(args):
    lat1 = None
    lon1 = None
    lat2 = None
    lon2 = None

    for i in range(1, len(sys.argv)):
	arg = sys.argv[i]

	if lon1 is None:
	    lon1 = arg
        elif lat1 is None:
            lat1 = arg
        elif lon2 is None:
            lon2 = arg
        elif lat2 is None:
            lat2 = arg
	else:
	    usage()
     
    if (lon1 and lat1 and lon2 and lat2):
        return lon1,lat1,lon2,lat2   
    else:
        print "great_circle lon1 lat1 lon2 lat2"
        sys.exit(1)

def greatCircle(lon1,lat1,lon2,lat2,units="mi"):
    if units=='mi': 
        radius = 3956
    elif units=='km':
        radius = 6367
    else:
        return None

    a = (90-float(lat1))*(pi/180)
    b = (90-float(lat2))*(pi/180)
    theta = (float(lon2)-float(lon1))*(pi/180)
    c = math.acos((math.cos(a)*math.cos(b)) +
                  (math.sin(a)*math.sin(b)*math.cos(theta)))
    return radius*c

if __name__ == "__main__":
    lon1,lat1,lon2,lat2 = getArgs(sys.argv)
    print 
    print "Distance* between (",lon1,lat1,") and (",lon2,lat2,")"
    d = greatCircle(lon1,lat1,lon2,lat2)
    print d,"miles"
    print d*1.609344,"kilometers"
    print
    print " * along a great circle assuming a sphere with radius of 3956 miles"
