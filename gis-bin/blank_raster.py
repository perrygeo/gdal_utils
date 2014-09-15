#!/usr/bin/env python
"""
 blank_raster.py
 Makes a blank raster

 Author: Matthew T. Perry

 License: You are free to use or modify this code for any purpose.
          This license grants no warranty of any kind, express or implied. 
"""
import sys
import numpy
from osgeo import gdal

def create_blank_raster(extent,cellsize,outfile,format):
    """
    Creates a blank raster dataset with all zeros
    """
    ydist = extent[3] - extent[1]
    xdist = extent[2] - extent[0]
    xcount = int((xdist/cellsize)+1)
    ycount = int((ydist/cellsize)+1)

    # Create the blank numpy array
    outArray = numpy.zeros( (ycount, xcount) )

    # Create output raster  
    driver = gdal.GetDriverByName( format )
    dst_ds = driver.Create( outfile, xcount, ycount, 1, gdal.GDT_Float32 )

    # This is bizzarly complicated
    # the GT(2) and GT(4) coefficients are zero,     
    # and the GT(1) is pixel width, and GT(5) is pixel height.     
    # The (GT(0),GT(3)) position is the top left corner of the top left pixel
    gt = (extent[0],cellsize,0,extent[3],0,(cellsize*-1.))
    dst_ds.SetGeoTransform(gt)
    
    dst_band = dst_ds.GetRasterBand(1)
    dst_band.WriteArray(outArray,0,0)
    print
    print "Created blank output %s at %s" % (format, outfile)


if __name__ == "__main__":
    extent = [-180., -90., 180., 90.]
    cellsize = 1 
    outfile = "test.tif"
    format = "GTiff"
    print "Calling the following python function for testing:"
    print "   create_blank_raster([-180., -90., 180., 90.], 1, 'test.tif', 'GTiff')"
    print
    print "   create_blank_raster(extent, cellsize, output, format)"
    create_blank_raster(extent, cellsize, outfile, format)
