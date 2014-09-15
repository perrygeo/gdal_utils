#!/bin/sh
#
# Authors: J Hudson (Sept 9 2006), Matthew Perry
# posted comment to http://www.perrygeo.net/wordpress/?p=7
#
if [ ! $1 ] ; then
 echo 
 echo "mkrelief.sh [input dem] {output - defaults to hillrelief.tif}"
 echo 
 exit
fi

INFILE=$1
OUTFILE=${2:-hillrelief.tif}
PID=$$
SCALE=/home/perry/src/perrygeo/demtools/scale.txt

hillshade $INFILE .s_$PID.tif -s 370400 -z 20
color-relief $INFILE $SCALE .c_$PID.tif
listgeo .s_$PID.tif > .info_$PID.dat
# The ugly bit. Via a GIF to force 256 colours
# Otherwise QGIS looks very strange
composite -blend 50 .c_$PID.tif .s_$PID.tif .geo_$PID.gif
convert .geo_$PID.gif .geo_$PID.tif
geotifcp -g .info_$PID.dat .geo_$PID.tif $OUTFILE
rm -f .s_$PID.tif .c_$PID.tif .geo_$PID.gif .geo_$PID.tif .info_$PID.dat



