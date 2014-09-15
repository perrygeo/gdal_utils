#!/usr/bin/env python
# gdal_catalog.py
# Purpose: Catalog all raster datasources found in a directory tree
# Usage: python gdal_catalog.py <path> <output prefix> <forcegeo{0|1}> ... usage() for examples
# Creates prefix_ds.txt in | pipe delimited format
# Authors: Tyler Mitchell, Matthew Perry, Jan-2006
#
# Known bugs:
#  If a single raster datasource can be opened through more than one file,
#    it will be counted multiple times (ArcInfo Grids, others?..)
#
# update: 1/27/2004 mp
#  Added support for statistics per raster band
#

import gdal, ogr, os, sys

def usage():
  print
  print " gdal_catalog.py <path> {output prefix} {forcegeo(0|1)}"
  print
  print " examples:"
  print "  python gdal_catalog.py /home/user/data"
  print "  python gdal_catalog.py /home/user/data myrastercatalog 1"
  print
  sys.exit(1)

def walkall(walkloc,dsfileout,bdfileout,forcegeo):
  # The following counters will be used for generating
  #  unique datasource and layer ids (i.e. primary keys)
  dscounter = 0

  # Open up the output files and output header row
  dsfileout.write('dsid|rasterpath|bandcount|geotransform|drivername|xnumpixels|ynumpixels|projectionwkt\n')
  bdfileout.write('dsid|bandid|min|max|overviews\n')

  # Start walking through all the folders in specified path
  for walkdirs in walkloc:
    topdir = walkdirs[0]
    dirs = walkdirs[1]
    files = walkdirs[2]
    for walkdir in dirs:
      currentpath = os.path.join(topdir,walkdir)
      if (checkds(currentpath,forcegeo)):
        dscounter += 1
        details,bandcount,ds = getdsdetails(currentpath)
        dsfileout.write('|'.join([str(dscounter),details]))
        dsfileout.write('\n')
        for bandnum in range(1,bandcount+1):
          details = getbanddetails(ds,bandnum)
          bdfileout.write('|'.join([str(dscounter),str(bandnum),details])) 
          bdfileout.write('\n');
    for walkfile in files:
      currentfile = os.path.join(topdir,walkfile)
      if (checkds(currentfile,forcegeo)):
        dscounter += 1
        details,bandcount,ds = getdsdetails(currentfile)
        dsfileout.write('|'.join([str(dscounter),details]))
        dsfileout.write('\n')
        for bandnum in range(1,bandcount+1):
          details = getbanddetails(ds,bandnum)
          bdfileout.write('|'.join([str(dscounter),str(bandnum),details])) 
          bdfileout.write('\n');
          

def checkds(filepath,forcegeo):
  ds = gdal.OpenShared(filepath)
  if ds is not None:
    if forcegeo == 1 and ds.GetGeoTransform() == (0, 1, 0, 0, 0, 1):
      return False
    else:
      return True
  else:
    return False

def getdsdetails(filepath):
  ds = gdal.OpenShared(filepath) 
  print "*Calculating dataset stats for raster ",filepath
  bandcount = ds.RasterCount
  geotrans = ds.GetGeoTransform()
  driver = ds.GetDriver().LongName
  wkt = ds.GetProjection()
  rasterx = ds.RasterXSize
  rastery = ds.RasterYSize  
  dsstring = '|'.join([filepath, str(bandcount), str(geotrans),str(driver),str(rasterx),str(rastery),wkt])
  return dsstring, bandcount, ds

def getbanddetails(ds,bandnum):
  band = ds.GetRasterBand(bandnum)
  print "*  Calculating band stats for band number ",bandnum
  min,max = band.ComputeRasterMinMax()
  overviews = band.GetOverviewCount()
  bdstring = '|'.join([str(min),str(max),str(overviews)])
  return bdstring

if __name__ == '__main__':
  # This disables error messages to stdout when a datasource can't
  #  be opened
  gdal.PushErrorHandler()

  try:
    basepath = sys.argv[1]
  except:
    usage()

  # Do we require that all raster sources have a geographic transformation?
  # forcegeo = 1  => yes
  try:
    forcegeo = sys.argv[3]
  except:
    forcegeo = 0

  # Set up the output file that will be created
  try:
    prefix = sys.argv[2]
  except:
    prefix = 'raster'
  dstxt = '_'.join([prefix,'rds.txt'])
  bdtxt = '_'.join([prefix,'rbd.txt'])
  print ' '.join(['*Opening output files:',dstxt,bdtxt])
  print ' '.join(['*Searching',basepath,'for raster datasets ...'])
  dsfileout = open(dstxt, 'w')
  bdfileout = open(bdtxt, 'w')

  # Below, walkloc holds a list of a string and two arrays:
  #   walkloc.next[0] - top level "current" walk dir (string)
  #   walkloc.next[1] - array of all other dirs in [0]
  #   walkloc.next[2] - array of all files in [0]
  #   walkloc.next cycles through every folder in [1]
  # Top dir comes from 1st command line argument
  walkloc = os.walk(basepath)
  walkall(walkloc,dsfileout,bdfileout,forcegeo)

  #cleanup
  print ' '.join(['*Closing output files:',dstxt,bdtxt])
  dsfileout.close()
