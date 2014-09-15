#!/usr/bin/python
"""
This script converts the US National Hydrography dataset (NHD) to OSM format
NHD is available for download by watershed/basin in shapefile format 
at http://nhd.usgs.gov/data.html)

CURRENTLY IMPLEMENTED (NHD:FTYPE -> OSM:Tags): 
Flowline:StreamRiver -> waterway:stream
Flowline:ArtificialPath (etc) -> waterway:canal
Flowline:Pipeline -> man_made:pipeline;type:water
Waterbody:SwampMarsh -> natural:marsh
Waterbody:Reservoir -> natural:water;man_made:reservoir
Waterbody:LakePond -> natural:water

- Uses GNIS_NAME as name tag if available.
- Applies oneway:true tag to streams and rivers to indicate flow direction

TODO:
 - For polygon waterbodies, need to incorporate holes 
 - incorporate all dbf fields
 - map the full NHD schema to osm features/tags
   (full desc of NHD schema:  http://nhd.usgs.gov/chapter2/index.html )

Based heavily on script by christopher schmidt -
 http://boston.freemap.in/osm/files/mgis_to_osm.py
Modified by Matt Perry
"""

VERSION="0.1"

from osgeo import ogr
from osgeo import osr

def parse_flowline_for_nhd( filename ):
    dr = ogr.GetDriverByName("ESRI Shapefile")
    poDS = dr.Open( filename )

    if poDS == None:
        raise "Open failed."

    poLayer = poDS.GetLayer( 0 )

    poLayer.ResetReading()

    ret = []

    poFeature = poLayer.GetNextFeature()
    while poFeature:
        tags = {}
        
        ftype = str(poFeature.GetField("FTYPE"))
        print ftype
        if ftype != "Coastline": 
            if ftype == "StreamRiver": 
                tags["waterway"] = "stream"
            elif ftype == "ArtificialPath" \
              or ftype == "CanalDitch" \
              or ftype == "Connector":
                tags["waterway"] = "canal"
            elif ftype == "Pipeline":
                tags["man_made"] = "pipeline"
                tags["type"] = "water"
            else:
                tags["waterway"] = "unclassified"

            gnisname = str( poFeature.GetField("GNIS_Name"))
            if gnisname != "None":
                tags["name"] = gnisname

            flowdir = str( poFeature.GetField("FLOWDIR"))
            if flowdir == "With Digitized":
                tags["oneway"] = "true"

            # SEGMENT ID
            tags["nhd:seg_id"] = int( poFeature.GetField("ComID") )
        
            # STREET ID
            tags["nhd:way_id"] = int( poFeature.GetField("ReachCode") )

            # COPY DOWN THE GEOMETRY
            geom = []
        
            rawgeom = poFeature.GetGeometryRef()
            #print dir( rawgeom )
            for i in range( rawgeom.GetPointCount() ):
                geom.append( (rawgeom.GetX(i), rawgeom.GetY(i)) )
    
            ret.append( (geom, tags) )
        
        poFeature = poLayer.GetNextFeature()
        
    return ret


def parse_waterbody_for_nhd( filename ):
    dr = ogr.GetDriverByName("ESRI Shapefile")
    poDS = dr.Open( filename )

    if poDS == None:
        raise "Open failed."

    poLayer = poDS.GetLayer( 0 )

    poLayer.ResetReading()

    ret = []

    poFeature = poLayer.GetNextFeature()
    while poFeature:
        tags = {}
        
        ftype = str(poFeature.GetField("FTYPE"))
        print ftype
        if ftype != "SeaOcean":
            if ftype == "SwampMarsh": 
                tags["natural"] = "marsh"
            elif ftype == "Reservoir":
                tags["natural"] = "water"
                tags["landuse"] = "reservoir" 
            elif ftype == "LakePond":
                tags["natural"] = "water"

            gnisname = str( poFeature.GetField("GNIS_Name"))
            if gnisname != "None":
                tags["name"] = gnisname

            # SEGMENT ID
            tags["nhd:seg_id"] = int( poFeature.GetField("ComID") )
        
            # STREET ID
            tags["nhd:way_id"] = int( poFeature.GetField("ComID") )

            # COPY DOWN THE GEOMETRY
            geom = []
        
            rawgeom = poFeature.GetGeometryRef()
            # TODO: this just copies the outer polygon, not any holes!
            # rawgeom.GetGeometryCount()
            subgeom = rawgeom.GetGeometryRef(0) 
            for j in range( subgeom.GetPointCount() ):
                geom.append( (subgeom.GetX(j), subgeom.GetY(j)) )
    
            ret.append( (geom, tags) )
        
        poFeature = poLayer.GetNextFeature()

    return ret



from_proj = osr.SpatialReference()
#from_proj.ImportFromWkt( boston_wkt )
from_proj.SetWellKnownGeogCS( "EPSG:4326" )

to_proj = osr.SpatialReference()
to_proj.SetWellKnownGeogCS( "EPSG:4326" )

tr = osr.CoordinateTransformation( from_proj, to_proj )

def unproject( point ):
    pt = tr.TransformPoint( point[0], point[1] )
    return (pt[1], pt[0])

def round_point( point, accuracy=6 ):
    return tuple( [ round(x,accuracy) for x in point ] )

def compile_nodelist( parsed_massgis, first_id=1 ):
    nodelist = {}
    
    i = first_id
    for geom, tags in parsed_massgis:
        if len( geom )==0:
            continue
        
        for point in geom:
            r_point = round_point( point )
            if r_point not in nodelist:
                nodelist[ r_point ] = (i, unproject( point ))
                i += 1
            
    return (i, nodelist)

def adjacent( left, right ):
    left_left = round_point(left[0])
    left_right = round_point(left[-1])
    right_left = round_point(right[0])
    right_right = round_point(right[-1])
    
    return ( left_left == right_left or
             left_left == right_right or
             left_right == right_left or
             left_right == right_right )
             
def glom( left, right ):
    
    left = list( left )
    right = list( right )
    
    left_left = round_point(left[0])
    left_right = round_point(left[-1])
    right_left = round_point(right[0])
    right_right = round_point(right[-1])
    
    if left_left == right_left:
        left.reverse()
        return left[0:-1] + right
        
    if left_left == right_right:
        return right[0:-1] + left
        
    if left_right == right_left:
        return left[0:-1] + right
        
    if left_right == right_right:
        right.reverse()
        return left[0:-1] + right
        
    raise 'segments are not adjacent'

def glom_once( segments ):
    if len(segments)==0:
        return segments
    
    unsorted = list( segments )
    x = unsorted.pop(0)
    
    while len( unsorted ) > 0:
        n = len( unsorted )
        
        for i in range(0, n):
            y = unsorted[i]
            if adjacent( x, y ):
                y = unsorted.pop(i)
                x = glom( x, y )
                break
                
        # Sorted and unsorted lists have no adjacent segments
        if len( unsorted ) == n:
            break
            
    return x, unsorted
    
def glom_all( segments ):
    unsorted = segments
    chunks = []
    
    while unsorted != []:
        chunk, unsorted = glom_once( unsorted )
        chunks.append( chunk )
        
    return chunks
        
                

def compile_waylist( parsed_massgis, blank_way_id ):
    waylist = {}
    
    #Group by massgis:way_id
    for geom, tags in parsed_massgis:
        way_key = tags.copy()
        del( way_key['nhd:seg_id'] )
        way_key = ( way_key['nhd:way_id'], tuple( [(k,v) for k,v in way_key.iteritems()] ) )
        
        if way_key not in waylist:
            waylist[way_key] = []
            
        waylist[way_key].append( geom )
    
    ret = {}
    for (way_id, way_key), segments in waylist.iteritems():
        
        if way_id != blank_way_id:
            ret[way_key] = glom_all( segments )
        else:
            ret[way_key] = segments
        
    return ret
            

import time
from xml.sax.saxutils import escape
def nhd_to_osm( nhddir, osm_filename, blank_way_id ):
    
    import_guid = time.strftime( '%Y%m%d%H%M%S' )

    print "parsing Flowline file"
    parsed_flowline = parse_flowline_for_nhd( os.path.join(nhddir, "hydrography/NHDFlowline.shp"))

    print "parsing Waterbody file"
    parsed_waterbody =  parse_waterbody_for_nhd( os.path.join(nhddir, "hydrography/NHDWaterbody.shp"))

    parsed_features = parsed_flowline + parsed_waterbody

    print "compiling nodelist"
    i, nodelist = compile_nodelist( parsed_features )
    
    print "compiling waylist"
    waylist = compile_waylist( parsed_features, blank_way_id )
    
    print "constructing osm xml file"
    ret = []
    ret.append( "<?xml version='1.0' encoding='UTF-8'?>" )
    ret.append( "<osm version='0.5' generator='JOSM'>" )
    
    for id, (lat, lon) in nodelist.values():
        ret.append( "  <node id='-%d' action='create' visible='true' lat='%f' lon='%f' >" % (id, lat, lon) )
        ret.append( "    <tag k=\"source\" v=\"nhd_import_v%s\" />" % VERSION  )
        ret.append( "    <tag k=\"attribution\" v=\"USGS NHD\" />" )
        ret.append( "  </node>" )
        
    for waykey, segments in waylist.iteritems():
        for segment in segments:
            ret.append( "  <way id='-%d' action='modify' visible='true'>" % i )
            
            ids = [ nodelist[ round_point( point ) ][0] for point in segment ]
            for id in ids:
                ret.append( "    <nd ref='-%d' />" % id )
                
            for k, v in waykey:
                ret.append( "    <tag k=\"%s\" v=\"%s\" />" % (k, escape(str(v))) )
                ret.append( "    <tag k=\"source\" v=\"nhd_import_v%s_%s\" />" % (VERSION, import_guid) )
                ret.append( "    <tag k=\"attribution\" v=\"USGS NHD\" />" )
                
            ret.append( "  </way>" )
            
            i += 1
        
    ret.append( "</osm>" )
    
    print "writing to disk"
    fp = open( osm_filename, "w" )
    fp.write( "\n".join( ret ) )
    fp.close()
    
if __name__ == '__main__':
    import sys, os.path
    if len(sys.argv) < 3:
        print "%s nhd-directory output.osm" % sys.argv[0]
        sys.exit()
    nhddir = sys.argv[1]
    if not os.path.exists(os.path.join(nhddir, "hydrography/NHDFlowline.shp")):
        print "probably not a valid NHD directory"
        sys.exit()
    osm = sys.argv[2]
    id = os.path.basename(os.path.split(nhddir)[0])
    nhd_to_osm( nhddir, osm, id )
