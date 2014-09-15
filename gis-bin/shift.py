#!/usr/bin/env python
import ogr
import sys
import os

def usage():
    print
    print 'shift.py input_file x_shift y_shift output_file'
    print '  input_file  : any supported OGR vector data source'
    print '  x_shift     : Amount to add to each X'
    print '  y_shift     : Amount to add to each Y'
    print '  output_file : shapfile output'
    print 'Author: Matthew T. Perry Sept. 21, 2005 '
    print 
    sys.exit(1)

def error(message):
    print
    print message
    print
    sys.exit(1)

def getArgs(args):
    infile = None
    xshift = None
    yshift = None
    outfile = None

    for i in range(1, len(sys.argv)):
	arg = sys.argv[i]

	if infile is None:
	    infile = arg
            if (not os.path.exists(infile)):
                error('The input file "' + infile +'" does not exist') 
        elif xshift is None:
            xshift = arg
        elif yshift is None:
            yshift = arg
        elif outfile is None:
            outfile = arg  
            if (os.path.exists(outfile)):
                error('The output file "' + infile +'" already exists')  
	else:
	    usage()
     
    if (infile is not None):
        return infile, xshift, yshift, outfile
    else:
        usage()    

def shift( geom, xshift , yshift ):
    for i in range( geom.GetGeometryCount() ):
        subgeom = geom.GetGeometryRef(i)
	for p in range( subgeom.GetPointCount() ):
            newx = subgeom.GetX(p) + float(xshift)
            newy = subgeom.GetY(p) + float(yshift)
            subgeom.SetPoint(p, newx, newy)
                
    return geom

def CloneLayer ( ds, src_layer ):
    ''' create output layer as a clone of source layer '''
    defn = src_layer.GetLayerDefn()

    dest_layer = ds.CreateLayer( 
	defn.GetName(), src_layer.GetSpatialRef(), defn.GetGeomType()  )

    for i in range( defn.GetFieldCount() ):
	src_fd = defn.GetFieldDefn( i )
	dest_fd = ogr.FieldDefn( src_fd.GetName(), src_fd.GetType() )
	dest_fd.SetWidth( src_fd.GetWidth() )
	dest_fd.SetPrecision( src_fd.GetPrecision() )
	dest_layer.CreateField( dest_fd )

    return dest_layer
    
if __name__ == "__main__":
    infile, xshift, yshift, outfile = getArgs(sys.argv);

    # Open dataset
    ds = ogr.Open(infile)
    layer=ds.GetLayer()

    # Create output dataset/layer
    driver = ogr.GetDriverByName('ESRI Shapefile')
    #driver.DeleteDataSource(outfile)
    outds = driver.CreateDataSource(outfile)
    outlayer = CloneLayer( outds, layer )

    # Loop thru features: clone attributes, 
    #   shift geometries and create output feature
    feature = layer.GetNextFeature()
    while feature is not None:
	outfeature = ogr.Feature(feature_def=outlayer.GetLayerDefn())

        # Loop thru fields and clone attributes
	field_count = layer.GetLayerDefn().GetFieldCount()
	for i in range(field_count):
	    outfeature.SetField( i, feature.GetField(i) )
 
        # create shifted geometry      
        geom = shift( feature.GetGeometryRef() , xshift , yshift )
 	outfeature.SetGeometry( geom )

        #Write the feature 
	outlayer.CreateFeature( outfeature )

        # Clean house and continue loop
        feature.Destroy()
        outfeature.Destroy()
        feature = layer.GetNextFeature()     


    # Close out the datasources
    ds.Destroy()
    outds.Destroy()
