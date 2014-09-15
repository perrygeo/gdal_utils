#!/usr/bin/env python
"""
 Raster Query
 Function to grab raster values based on coordinates
 Matthew Perry
 Apache 2.0 License
"""

import gdal
import Numeric
import sys

def getRasterValue(x,y,datasource,window=3,bandnum=1):
    ds = gdal.Open(datasource)
    band = ds.GetRasterBand(bandnum)
    gt = ds.GetGeoTransform()
    xoff = int((x - gt[0]) / gt[1]) - int(window/2) 
    yoff = int((y - gt[3]) / gt[5]) - int(window/2) 
    xsize = window 
    ysize = window 
    try:
        a = band.ReadAsArray( xoff, yoff, xsize, ysize)
        avg_value = Numeric.sum( Numeric.sum(a) ) / Numeric.size(a)
        return avg_value
    except:
        print "Coordinates out of range"
        return None

    
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print
        print " ./rasterQuery.py -119.5 34.5 '/home/perry/data/sbdata/sbdems/sbdems.tif'"
        print
        sys.exit(1)
    
    rasterval = getRasterValue( float(sys.argv[1]), float(sys.argv[2]), sys.argv[3])
    print "Raster value (band 1):", rasterval
