#!/bin/bash
cd /home/perry/active/osm

export POSTGIS_SRC=/usr/share/postgresql/8.2/contrib/postgis-1.3.2

dropdb sbosm

createdb sbosm

createlang -d sbosm plpgsql

psql -d sbosm -f ${POSTGIS_SRC}/lwpostgis.sql

psql -d sbosm -f ${POSTGIS_SRC}/spatial_ref_sys.sql



#wget -O sb.osm "http://perrygeo%40gmail%2Ecom:osmosmosm@www.openstreetmap.org/api/0.5/map?bbox=-119.945,34.375,-119.55,34.55"
osm2pgsql -d sbosm sb.osm
osm2pgsql -a -d sbosm /home/perry/active/nhd_to_osm/nhd.osm
psql -d sbosm -f /home/perry/src/perrygeo/mapserver/setup_z_order.sql
cd shp
rm *.*
ogr2ogr -s_srs "EPSG:3395" -t_srs "EPSG:4326" sb_points.shp  "PG:dbname=sbosm" planet_osm_point
ogr2ogr -s_srs "EPSG:3395" -t_srs "EPSG:4326" sb_lines.shp "PG:dbname=sbosm" planet_osm_line
ogr2ogr -s_srs "EPSG:3395" -t_srs "EPSG:4326" sb_polygons.shp "PG:dbname=sbosm" planet_osm_polygon
echo
echo "Now run /usr/local/bin/generate_tiles.py and look in ~/osm/tiles or http://localhost/osm.html"
echo