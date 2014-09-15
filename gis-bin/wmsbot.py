#!/usr/bin/python
#############################################################
# WMSbot Version 0.1 Beta
#-----------------------------------------------------------
# Author: Matthew Perry
# Date: 10/29/04
# Description:
#  A web crawler that retrieves images from a remote WMS server
#  and creates a local dataset and WMS server (using Mapserver) 
#
# INPUT: WMS server url, overall extent, request format,
#       layer, output directory, cellsize[x,y],
#       imagesize[x,y], output file extension, prefix,
#       wld file extension, srs, wms online resource url
#
# OUTPUT: Georeferenced image "tiles" covering the given extent,
# 	A tileindex shapefile for all images and
# 	a mapfile.. ready to go as a local WMS server!
#
# REQUIREMENTS:
# 	python 
#	gdaltindex (an executable compiled with GDAL)
#	gdaladdo ( " )
# 	mapserver 4.x (with WMS-server support)
#
# TO DO:
#   ? error handling (no image returned, files already exist, invalid directory)    
#   ? Option to suppress verbose output
#   ? JPEGs look crumy around the seams; reformat images using GDAL (converting to TIFFs) 
#   ? Terraserver images have the USGS logo on each tile
#   ? Support for command line args AND/OR configuration file, GUI or interactive prompt
#   ? gdaladdo & gdaltindex are called through os.system.. should use python GDAL module instead
#   ? Write out example LAYER entry for mapserver WMS client 
#   ? Support for re-projection with proj4/pyproj 
##############################################################
import urllib, os


# Variables (Eventually use command line args)
##############################################################

# WMS properties (obtain from GetCapabilities?)
################
wmsurl= 'http://onearth.jpl.nasa.gov/wms.cgi?request=GetMap&version=1.1.1&layers=global_mosaic&SRS=EPSG:4326&styles=visual'
# extent = [472640,4599055,480640,4605614]
extent = [-123.329191010517,41.5444522809372,-122.233485453041,42.6037674442837]
format = 'image/jpeg'
layers = 'global_mosaic'

# Output properties
###################
extension = 'jpg'
wldextension = 'wld'
prefix = 'landsat_visual'
outdir = '/maps/wmsbot/landsat_visual/'
cellsize = [0.00014,0.00014] #aprox 1/2 second
imagesize = [800.00,700.00]
srs = 'EPSG:4326'
wmsonlineresource = 'http://klamath.humboldt.edu/cgi-bin/mapserv?map=' + outdir + prefix + '.map' 
ovr = 1  		# do we build overviews??
ovrlevel = '2 4 8 16' 

# MAIN 
##############################################################

#Calculate the overall dimensions
#####################
ydist = extent[3] - extent[1]
xdist = extent[2] - extent[0]

print "xdist", xdist
print "ydist", ydist
print "cellsize[0]", cellsize[0]
print "cellsize[1]", cellsize[1]
print "imagesize[0]", imagesize[0]
print "imagesize[1]", imagesize[1]

#Calculate number of images needed to cover the area
#####################
xcount = int((xdist/(cellsize[0]*imagesize[0]))+1)
ycount = int((ydist/(cellsize[1]*imagesize[1]))+1)
imgcount = (xcount)*(ycount)
z = 1 				

msg = 'Retrieving ' + str(imgcount) + ' ' + extension + ' images (' + str(imagesize[0]) + ' x ' + str(imagesize[1]) + ')\nfrom ' + wmsurl + ' =>'
print msg

# Calculate extent of each image, fetch & save to local disk with wld file
######################
for ypos in range(ycount):
    for xpos in range(xcount):
        # create a 4-item list of extents (buffered by cellsize)
	##############
        x1 = xpos * imagesize[0] * cellsize[0] + extent[0] - cellsize[0]
        y1 = ypos * imagesize[1] * cellsize[1] + extent[1] - cellsize[1]
        x2 = (xpos + 1) * imagesize[0] * cellsize[0] + extent[0]
        y2 = (ypos + 1) * imagesize[1] * cellsize[1] + extent[1]
        bbox = [x1, y1, x2, y2]
        
        # Get image
	###############
        url = wmsurl + '&LAYERS=' + layers + "&BBOX=" + str(bbox[0]) + ',' + str(bbox[1]) + ',' + str(bbox[2]) + ',' + str(bbox[3]) + '&HEIGHT=' + str(imagesize[1]) + '&WIDTH=' + str(imagesize[0]) + '&FORMAT=' + format
        file = outdir + prefix + '_' + str(xpos) + '_' + str(ypos) + '.' + extension
        urllib.urlretrieve(url, file)
        
        # write WLD file
	################ 
        wldfile = outdir + prefix + '_' + str(xpos) + '_' + str(ypos) + '.' + wldextension
        wldparam = [cellsize[0], 0, 0, (cellsize[1]*-1), x1, y2]
        wld = open(wldfile,'w')
        for i in wldparam:
            line = str(i) + '\n'
            wld.write(line)
        wld.close() 
	
	#create overviews
	#########################
	if ovr == 1:
		ovrcmd = 'gdaladdo -r average ' + file + ' ' + ovrlevel
		os.system(ovrcmd)

	#print message
	msg = ' (' + str(z) + ') wrote ' + file + ' & ' + wldfile
	z = z+1
	print msg
	print url
       
#clean http cache
#################
urllib.urlcleanup()

msg = 'Finished downloading images to ' + outdir
print msg

#create tileindex
#########################
tileshp = prefix + '_tile.shp'
tilecmd = 'gdaltindex ' + outdir + tileshp + ' ' + outdir + '*.' + extension
os.system(tilecmd)

msg = 'Created tileindex shapefile at ' + outdir + tileshp
print msg

#output WMS server mapfile
###########################
maptext = """### Mapfile generated by wmsbot ###
MAP
  NAME "%s"
  EXTENT %s %s %s %s
  SIZE 600 480
  SHAPEPATH "."
  UNITS meters
  IMAGETYPE %s

  WEB
    IMAGEPATH "/tmp/"
    IMAGEURL "/ms_tmp/"
    METADATA
      "wms_title"    "%s"
      "wms_onlineresource"    "%s"
      "wms_srs"    "%s"
    END
  END

  LAYER
    NAME "%s"
    STATUS ON
    TILEINDEX "%s"
    TILEITEM "location"
    TYPE RASTER
    METADATA
      "wms_title"    "%s"
      "wms_srs"    "%s"
      "wms_abstract" ""
    END
  END
END

""" % (prefix, extent[0], extent[1], extent[2], extent[3], format, prefix, wmsonlineresource, srs, prefix, tileshp, prefix, srs)

# write mapfile
mappath = outdir + prefix + '.map'
mapfile = open(mappath,'w')
mapfile.write(maptext)
mapfile.close()

msg = 'Created WMS server mapfile at ' + mappath
print msg

# Output final message
########################
msg = """Try this URL to test the local server:
- %s&request=GetMap&version=1.1.1&layers=%s
or if you have Mapserver Web Client (mwc) installed, try:
- http://localhost/mwc.php?template=template3&map=%s

WMSbot completed successfully!!
""" % (wmsonlineresource,prefix,mappath)
print msg

