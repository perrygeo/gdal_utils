#!/bin/bash
# Usage:
#  cd to directory containing shps
#  shpmerge <outlayer> [to_srs] [source_srs]
#
# TO DO:
#  Check for valid input and handle outputlayer.shp
#  Check that outputlayer.shp doesn't alreadey exist
#  Allow user-supplied list of shps


if [ ! $1 ] ; then
 echo
 echo "shpmerge"
 echo "--------"
 echo "Description: merges all the shapefiles in the current directory into a single output shapefile"
 echo "Usage: shpmerge <outlayer> [to_srs] [source_srs]"
 echo 'Notes: outlayer must be the file prefix only (eg. "roads" NOT "roads.shp")'
 echo "Example:   "
 echo 
 echo "    shpmerge newlayer EPSG:4326 EPSG:26745"
 echo 
 echo '   (this will take all shps in the curent directory, reproject them from state plane to latlong and merge them into newlayer.shp)'
 echo 
 exit
fi

output_layer=$1
update_options=''
nln_options=''

if [ $2 ] ; then 
 proj_options="-t_srs $2"
fi

if [ $3 ] ; then
 proj_options="$proj_options -s_srs $3"
fi

for layer in `ls -1 *.shp | sed -e 's/\.shp$//'`; do
  ogr2ogr $proj_options $update_options $output_layer.shp $layer.shp $nln_options $layer
  update_options="-update -append"
  nln_options="-nln $output_layer"
done
