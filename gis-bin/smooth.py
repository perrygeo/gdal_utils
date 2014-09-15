#!/usr/bin/env python
import gdal
import Numeric
import sys
from math import sqrt

#####
# TO DO: 
# output floating point data
# change window size
# preserve edges (?)
#####


#**********************************#
#  Constants
noDataValue = -12345.0
debug = False

#**********************************#
#  Inputs
try:
    raster = sys.argv[1]
    outfile = sys.argv[2]
except:
    print "smooth.py raster outfile"

#**********************************#
#  Functions
def testNull(x,nodata):
    hasNull = False
    for i in x:
        if not i or i == nodata:
            return True
    return False

        
#**********************************#
#  Main
if __name__ == "__main__" :
    ds = gdal.Open(raster)

    inArray = ds.GetRasterBand(1).ReadAsArray()
    inNoDataValue = ds.GetRasterBand(1).GetNoDataValue()
  
    gt = ds.GetGeoTransform()

    outArray = Numeric.zeros( (ds.RasterYSize, ds.RasterXSize) ) 

    row = 0
    col = 0
    pixelnum = 0

    for i in inArray:
        for j in i:
            # Make c[0] empty so that we can use number scheme 
            # consistent with Grass source code 
            # (from which all of these algorithms are derived)
            # 3x3 window
            #  c1 c2 c3
            #  c4 c5 c6
            #  c7 c8 c9
            #
            total = 0
            hasNull = False
            try:
                c = ( 0, 
                      inArray[row-1][col-1],
                      inArray[row-1][col],
                      inArray[row-1][col+1],
                      inArray[row][col-1],
                      inArray[row][col],
                      inArray[row][col+1],
                      inArray[row+1][col-1],
                      inArray[row+1][col],
                      inArray[row+1][col+1] )
            except:
                # Probably means we're at an edge 
                hasNull = True
 
            if hasNull or testNull(c,inNoDataValue):
                # In this case, we bail and write null to the array
                Numeric.put(outArray,pixelnum,noDataValue)
                pixelnum += 1	
                col += 1
                continue
            
            for i in c:
                total += i
            
            Numeric.put(outArray,pixelnum,(total/9.0))         
                
            pixelnum += 1	
            col += 1

        row += 1
        col = 0

    # Output the Array
    format = "GTiff"
    driver = gdal.GetDriverByName( format )
    dst_ds = driver.Create( outfile, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Float32 )
    if ds.GetGeoTransform():
        dst_ds.SetGeoTransform(ds.GetGeoTransform())
    if ds.GetMetadata():
        dst_ds.SetMetadata(ds.GetMetadata())
    if ds.GetProjection():
        dst_ds.SetProjection(ds.GetProjection()) 
    dst_ds.GetRasterBand(1).SetNoDataValue( noDataValue )   
    dst_ds.GetRasterBand(1).WriteArray( outArray )

