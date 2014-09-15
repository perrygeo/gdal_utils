#!/bin/bash

if [ $# -ne 1 ]; then
  echo "make_clean_postgisdb.sh database-name"
  exit
fi

export POSTGIS_SRC=/usr/share

dropdb  $1

createdb  $1

createlang  -d $1 plpgsql

psql  -d $1 -f ${POSTGIS_SRC}/lwpostgis.sql 

psql  -d $1 -f ${POSTGIS_SRC}/spatial_ref_sys.sql
