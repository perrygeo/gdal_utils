# ogr_catalog5.py
# Purpose: Catalog all vector datasources/layers found in a directory tree
# Usage: python ogr_catalog4.py <path> <output prefix> <header comment char>
# Creates prefix_ds.txt, prefix_lay.txt in | pipe delimited format
# Author: Tyler Mitchell, Jan-2006

import gdal, ogr, os, sys

def walkall(walkloc,dsfileout,layfileout):
  # The following counters will be used for generating
  #  unique datasource and layer ids (i.e. primary keys)
  dscounter = 0
  layercounter = 0
  
  # Check if the user wants to comment the first/header line in the output
  # If so, use the character given in the 3rd argument
  if len(sys.argv) > 3:
    headercmt = sys.argv[3]
  else:
    headercmt = ''

  # Open up the output files
  dsfileout.write(''.join([headercmt,'dsid|datasource|format|layercount\n']))
  layfileout.write(''.join([headercmt,'layerid|dsid|datasource|format|layernumber|layername|featurecount|extent\n']))

  # Start walking through all the folders in specified path
  for walkdirs in walkloc:
    topdir = walkdirs[0]
    dirs = walkdirs[1]
    files = walkdirs[2]
    for walkdir in dirs:
      currentpath = os.path.join(topdir,walkdir)
      if (checkds(currentpath)):
        ds = ogr.OpenShared(currentpath)
        dscounter += 1
        try:
          dsdetails, dslcount = getdsdetails(currentpath, ds)
        except:
          print "** unable to get dataset details for", currentpath

        dsfileout.write('|'.join([str(dscounter),str(dsdetails),str(dslcount)]))
        dsfileout.write('\n')
        for laynum in range(dslcount):
          layercounter += 1
          layfileout.write('|'.join([str(layercounter),str(dscounter),str(getlayerdetails(currentpath,laynum,ds))]))
          layfileout.write('\n')
      for walkfile in files:
        currentfile = os.path.join(currentpath,walkfile)
        if (checkds(currentfile)):
          layercounter += 1
          layfileout.write('|'.join([str(layercounter),str(dscounter),str(getlayerdetails(currentfile,laynum,ds))]))
          layfileout.write('\n')

def checkds(filepath):
  try:
    ds = ogr.OpenShared(filepath)
    return True
  except ogr.OGRError:
    return False

def getdsdetails(filepath,ds):
  print ' '.join(['-SEARCHING:',filepath])
  if (filepath[-3:] not in skipext):
    #ds = ogr.OpenShared(filepath)
    dsname = ds.GetName()
    dsformat = ds.GetDriver().GetName()
    dslcount = ds.GetLayerCount()
    dsstring = '|'.join([dsname, dsformat])
    return dsstring, dslcount

def getlayerdetails(filepath,laynum,ds):
  if (filepath[-3:] not in skipext):
    #ds = ogr.OpenShared(filepath)
    dsstring, dslcount = getdsdetails(ds.GetName(),ds)
    details = ''
    layer = ds.GetLayer(laynum)
    layername = layer.GetName()
    print ' '.join(['--PROCESSING LAYER:',str(laynum),layername])
    layerfcount = str(layer.GetFeatureCount())
    layerextent = str(layer.GetExtent())
    details = "|".join( [dsstring,str(laynum),layername,layerfcount,str(layerextent)] )
    return details

if __name__ == '__main__':
  # This disables error messages to stdout when a datasource can't
  #  be opened
  gdal.PushErrorHandler()

  # Set which file extensions will be ignored as datasources  
  skipext = ('dbf','shx', 'xsd', 'tif', 'jpg', 'e00')

  # Set up the output file that will be created
  prefix = sys.argv[2]
  dstxt = '_'.join([prefix,'ds.txt'])
  laytxt = '_'.join([prefix,'lay.txt'])
  print ' '.join(['*Opening output files:',dstxt,laytxt])
  dsfileout = open(dstxt, 'w')
  layfileout = open(laytxt, 'w')

  # Below, walkloc holds a list of a string and two arrays:
  #   walkloc.next[0] - top level "current" walk dir (string)
  #   walkloc.next[1] - array of all other dirs in [0]
  #   walkloc.next[2] - array of all files in [0]
  #   walkloc.next cycles through every folder in [1]
  # Top dir comes from 1st command line argument
  #walkloc = os.walk('c:/temp/geobase') # for testing
  walkloc = os.walk(sys.argv[1])
  walkall(walkloc,dsfileout,layfileout)

  #cleanup
  print ' '.join(['*Closing output files:',dstxt,laytxt])
  dsfileout.close()
  layfileout.close()
