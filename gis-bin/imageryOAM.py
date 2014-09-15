"""
imageryOAM.py

Preprocess images for use in mapserver or Open Aerial Map. 
The idealized use case would be a large image in a compressed format in an non-geographic projection.
This script will chop the image into a number of geotiff tiles in latlong.
Overviews are built on the resulting images, completely null images are removed, and
a tileindex shapefile is built.

Example:
 python imagery2OAM.py bigUTM.sid 0.02 "+proj=utm +zone=10" output_tiledir mytile -119.98,-119.59,34.38,34.49

Caveats:
 this is currently just a hack and is not intended (yet) as a generic solution

Author: Matt Perry (perrygeo at gmail)
Last Modified: Dec 8, 2007
License: MIT
"""
import sys
import os
try:
    from numpy import arange
except ImportError:
    from Numeric import arange
try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import gdal
    import ogr
    import osr

BINDIR = "/opt/fwtools/bin_safe"
GDALWARP = os.path.join(BINDIR, "gdalwarp")
GDALTINDEX = os.path.join(BINDIR, "gdaltindex")
GDALINFO = os.path.join(BINDIR, "gdalinfo")
GDALADDO = os.path.join(BINDIR, "gdaladdo")
NULLVAL = 0.0
OVERLAP_FACTOR = 1./1000.
debug = True

if not os.path.exists(GDALWARP) or not os.path.exists(GDALTINDEX):
    usage("can't find the executables in %s" % BINDIR)

def usage(message=""):
    print "imagery2OAM.py source tilesize(degrees) source_proj4 output_directory basename {xmin,xmax,ymin,ymax}"
    print "example: \n   python imagery2OAM.py bigUTM.sid 0.02 \"+proj=utm +zone=10\" output_tiledir mytile -119.98,-119.59,34.38,34.49"
    print "\n", message
    sys.exit(1)

def get4326Extent(ds, src_proj4):
    src_gt = ds.GetGeoTransform()
    src_size = (ds.RasterXSize, ds.RasterYSize)
    minx = src_gt[0]
    miny = src_gt[3] + (src_gt[5]*src_size[1])
    maxx = src_gt[0] + (src_gt[1]*src_size[0])
    maxy = src_gt[3]
    wkt = 'POLYGON ((%f %f, %f %f, %f %f, %f %f, %f %f))' \
        % (minx, miny, minx, maxy, maxx, maxy, maxx, miny, minx, miny)
    if debug: print wkt
    g = ogr.CreateGeometryFromWkt(wkt)
    latlong = osr.SpatialReference()
    src_srs = osr.SpatialReference()
    latlong.ImportFromProj4("+init=epsg:4326")
    src_srs.ImportFromProj4(src_proj4)
    g.AssignSpatialReference(src_srs)
    g.TransformTo(latlong)
    return g.GetEnvelope()

def warpImage(src_proj4, extent, src_path, dest_path):
    cmd = "%s -s_srs '%s' -co \"TILED=YES\" -t_srs \"epsg:4326\" -of GTiff -r bilinear -te %f %f %f %f %s %s" % \
          (GDALWARP, src_proj4, extent[0], extent[2], extent[1], extent[3], src_path, dest_path)
    if debug: print cmd
    result = os.popen(cmd).read()
    return True

def isEntireRasterNull(path):
    ds = gdal.Open(path)
    if not ds:
        return False

    nullbandcount = 0
    for i in range(1,ds.RasterCount+1):
        if (NULLVAL,NULLVAL) == ds.GetRasterBand(i).ComputeRasterMinMax():
            nullbandcount += 1
    if nullbandcount == ds.RasterCount:
        return True
    else:
        return False
    
def main():
    if len(sys.argv) >= 5:
        src_path = sys.argv[1]
        tilesize = float(sys.argv[2])
        src_proj4 = sys.argv[3]    
        outdir = sys.argv[4]
        basename = sys.argv[5]
        try:
            extent = [float(x) for x in sys.argv[6].split(",")]
        except:
            extent = None
    else:
        usage()

    overlap = tilesize * OVERLAP_FACTOR
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    ds = gdal.Open(src_path)
    if not ds:
        usage("not a valid ds")

    if not extent:
        extent = get4326Extent(ds, src_proj4)
        print extent

    if debug:
        print extent
        print os.popen("%s %s" % (GDALINFO, src_path)).read()

    # Python's normal range function only works with ints
    # instead use Numeric or numpy's arange function
    lonlist = arange(extent[0],extent[1]+tilesize, tilesize)
    latlist = arange(extent[2],extent[3]+tilesize, tilesize)
    numtiles = len(lonlist) * len(latlist)
    counter = 0
    for i in lonlist:
        for j in latlist:
            counter += 1            
            filename = os.path.join(outdir, "%s_%s_%s.tif" % (basename, i, j))
            print "\n[%s / %s (%f  percent)] %s" % (counter, numtiles, 100.*(float(counter)/float(numtiles)), filename) 
            tile_extent = (i,i+tilesize+overlap,j,j+tilesize+overlap)
            warpImage(src_proj4, tile_extent, src_path, filename)
            if isEntireRasterNull(filename):
                os.remove(filename)
                if debug: print "tile %s was null - removed" % filename
                continue
            cmd = "gdaladdo -r average %s 2 4 8 16 32 64 128 256 512" % filename
            if debug: print cmd
            os.popen(cmd)
    # Hack alert ... *nix specific shell commands will fail on Windows. 
    cmd = "find %s -name '*.tif' | xargs %s %s" % \
          (outdir, GDALTINDEX, os.path.join(outdir,basename+"_index.shp"))
    if debug: print; print cmd
    os.popen(cmd)
    return 

if __name__ == "__main__":
    main()


