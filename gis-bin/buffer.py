#!/usr/bin/env python
"""
buffer.py 
Author: Matthew Perry
License: BSD
Date: 2007-12-10
see usage()
"""
import sys
import os
try:
    from osgeo import ogr
except ImportError:
    import ogr

def usage():
    print 'buffer.py'
    print 'Buffers a vector dataset by a specified distance.'
    print 'Usage: buffer.py buffer_distance infile outfile'
    print 'Example : buffer.py 20 streams.shp streams_buf20.shp '
    print 'Notes : '
    print '  - buffer_distance units are the same as the dataset coordinate system'
    print '  - output file must be shapefile (with the .shp extension)'
    print '  - Input can be points, lines or polygons. Output will always be polygon'
    print '  - All attributes from the original features will be carried over'
    sys.exit(1)

def error(message):
    print message
    sys.exit(1)

def getArgs(args):
    buffDist = None
    infile = None
    outfile = None

    for i in range(1, len(sys.argv)):
	arg = sys.argv[i]

	if buffDist is None:
	    buffDist = arg

	elif infile is None:
	    infile = arg
            if (not os.path.exists(infile)):
                error('The input file "' + infile +'" does not exist')  

	elif outfile is None:
	    outfile = arg
            if (os.path.exists(outfile)):
                error('The output file "' + outfile +'" already exists. Pick a different name.')        
	else:
	    usage()
     
    if (buffDist is not None and infile is not None and outfile is not None):
        return buffDist, infile, outfile
    else:
        usage()    

def CloneLayerForBuffer ( ds, src_layer ):
    ''' Modified function originally by Schuyler Erle <schuyler at nocat dot net>
        Used to create an copy of a dataset but always sets geomtype to polygon 
    '''
    defn = src_layer.GetLayerDefn()

    dest_layer = ds.CreateLayer( 
	defn.GetName(), src_layer.GetSpatialRef(), geom_type=ogr.wkbPolygon )

    for i in range( defn.GetFieldCount() ):
	src_fd = defn.GetFieldDefn( i )
	dest_fd = ogr.FieldDefn( src_fd.GetName(), src_fd.GetType() )
	dest_fd.SetWidth( src_fd.GetWidth() )
	dest_fd.SetPrecision( src_fd.GetPrecision() )
	dest_layer.CreateField( dest_fd )

    return dest_layer


if __name__ == "__main__":
    buffdist, infile, outfile = getArgs(sys.argv);

    # Open the input dataset and get the layer
    inDs = ogr.Open(infile)
    inLayer= inDs.GetLayer()

    # Create output dataset/layer
    driver = ogr.GetDriverByName('ESRI Shapefile')
    outDs = ogr.Open(outfile)
    if outDs:
        error(outfile + " already exists")
     
    outDs = driver.CreateDataSource(outfile)
    outLayer = CloneLayerForBuffer( outDs, inLayer )
 
    # Loop through input features, clone their attributes, buffer the geometry
    #   and add new the new buffered feature to output Layer
    inFeat = inLayer.GetNextFeature()
    while inFeat is not None:
	outFeat = ogr.Feature(feature_def=outLayer.GetLayerDefn())

        # Loop thru fields and clone attributes
	field_count = inLayer.GetLayerDefn().GetFieldCount()
	for i in range(field_count):
	    outFeat.SetField( i, inFeat.GetField(i) )

	outFeat.SetGeometry( inFeat.GetGeometryRef().Buffer(float(buffdist)) )
	outLayer.CreateFeature( outFeat )
	outFeat.Destroy()
	inFeat = inLayer.GetNextFeature()
    
    # Close the layer (is this necessary?)
    outLayer.SyncToDisk()

    # Close out the datasources
    outDs.Destroy()
    inDs.Destroy()
