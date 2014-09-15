#!/usr/bin/env python
"""
 point_density.py
 Calculate density of point data as a raster surface.
 Each raster cell contains a value indicating
 the number of points contained in the cell.
 
 To get decent performance on large vector datasets, the input vector dataset must
 have a gdal-recognized spatial index (ie a .qix file for shapefiles as created by shtree)

 Author: Matthew T. Perry

 License: You are free to use or modify this code for any purpose.
          This license grants no warranty of any kind, express or implied. 
"""
import ogr
import sys
import Numeric
import gdal

def getOpts():
    poly_ds = "/home/perry/data/world_cities/cities.shp"
    poly_lyr = 0
    extent = [-180., -90., 180., 90.]
    cellsize = 1 
    outfile = "/home/perry/Desktop/test2.tif"
    format = "GTiff"
    return (poly_ds,poly_lyr,extent,cellsize,outfile,format)    
   
if __name__ == "__main__":
    # Get the inputs
    (poly_ds,poly_lyr,extent,cellsize,outfile,format) = getOpts()    

    # Get the input layer
    ds = ogr.Open(poly_ds)
    lyr = ds.GetLayer(poly_lyr)
    
    # TODO: Confirm dataset is point and extents overlap 

    ydist = extent[3] - extent[1]
    xdist = extent[2] - extent[0]
    xcount = int(xdist/cellsize)
    ycount = int(ydist/cellsize)

    # Create output raster  
    driver = gdal.GetDriverByName( format )
    dst_ds = driver.Create( outfile, xcount, ycount, 1, gdal.GDT_Float32 )

    # the GT(2) and GT(4) coefficients are zero,     
    # and the GT(1) is pixel width, and GT(5) is pixel height.     
    # The (GT(0),GT(3)) position is the top left corner of the top left pixel
    gt = (extent[0],cellsize,0,extent[3],0,(cellsize*-1.))
    dst_ds.SetGeoTransform(gt)
    
    dst_band = dst_ds.GetRasterBand(1)
    dst_band.SetNoDataValue( -9999 )

    pixelnum = 0
    
    for ypos in range(ycount):
        # Create output line array
        outArray = Numeric.zeros( (1, xcount) )
        for xpos in range(xcount):
            # create a 4-item list of extents 
            minx = xpos * cellsize + extent[0] 
            maxy = extent[3] - ypos * cellsize 
            miny = maxy - cellsize
            maxx = minx + cellsize
            
            # Create Polygon geometry from BBOX
            wkt = 'POLYGON ((%f %f, %f %f, %f %f, %f %f, %f %f))' \
               % (minx, miny, minx, maxy, maxx, maxy, maxx, miny, minx, miny)
            g = ogr.CreateGeometryFromWkt(wkt)

            # Set spatial filter
            lyr.SetSpatialFilter(g)
                
            numfeatures = lyr.GetFeatureCount()
            #print wkt, numfeatures
            
            #Assign the number of features in the bbox
            # as value in line array
            #
            # NOTE: this is where one should test for an
            # actual intersection with the geos function
            # (ie loop through features
            # and ensure that the select features
            # actually intersect the cell geometry g)
            Numeric.put( outArray, xpos, numfeatures )
            lyr.ResetReading()

            pixelnum += 1
 
        print '%.2f pct complete' % (float(pixelnum)/(xcount*ycount) * 100.)
        dst_band.WriteArray(outArray,0,ypos)

