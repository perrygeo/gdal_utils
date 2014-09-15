#!/bin/bash

if [ $# -ne 2 ]; then
  echo "Usage: shp_rst.sh layer res"
  echo " must be shp prefix in current dir "
  exit
fi

v.in.ogr -o dsn=${1}.shp layer=$1 output=$1
g.region vect=$1
g.region res=$2
v.surf.rst input=$1 elev=${1}_rst smooth=9 zcolumn=elev

d.mon x1; d.rast ${1}_rst


