#!/usr/bin/env python
# calculate_area_field.py 
#
import sys
import ogr
import os

def usage():
    print
    print 'calculate_area_field.py input_file output_file new_field_name'
    print 'Author: Matthew T. Perry Sept. 17, 2005 '
    print 
    sys.exit(1)

def error(message):
    print
    print message
    print
    sys.exit(1)

def getArgs(args):
    infile = None
    outfile = None
    fieldname = None
    units = None
    proj = None

    for i in range(1, len(sys.argv)):
	arg = sys.argv[i]

	if infile is None:
	    infile = arg
            if (not os.path.exists(infile)):
                error('The input file "' + infile +'" does not exist')  
        
        elif outfile is None:
            outfile = arg
            if (os.path.exists(outfile)):
                error('The output file "' + outfile +'" already exists. Pick a different name.')
       
	elif fieldname is None:
	    fieldname = arg

	elif units is None:
	    units = arg

	elif proj is None:
	    units = arg
  
	else:
	    usage()
     
    if (infile is not None and outfile is not None and fieldname is not None):
        return infile, outfile, fieldname, units, proj
    else:
        usage()    

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
    infile, outfile, fieldname, units, proj = getArgs(sys.argv);

    # Open the input dataset and get the layer
    ds = ogr.Open(infile)
    layer= ds.GetLayer()

    # Create output dataset/layer
    driver = ogr.GetDriverByName('ESRI Shapefile')
    #driver.DeleteDataSource(outfile)
    outDs = driver.CreateDataSource(outfile)
    outLayer = CloneLayer( outDs, layer )

    # Add the new area field to the file
    fd = ogr.FieldDefn(fieldname, ogr.OFTReal)
    fd.SetWidth(20)
    fd.SetPrecision(8)
    outLayer.CreateField(fd)
    findex = outLayer.GetLayerDefn().GetFieldIndex(fieldname)	    

    # Loop through input features, clone their attributes, calculate geom
    feature = layer.GetNextFeature()
    while feature is not None:
	outFeat = ogr.Feature(feature_def=outLayer.GetLayerDefn())

        # Loop thru fields and clone attributes
	field_count = layer.GetLayerDefn().GetFieldCount()
	for i in range(field_count):
	    outFeat.SetField( i, feature.GetField(i) )
 
        # Clone geometry      
 	outFeat.SetGeometry( feature.GetGeometryRef())

        #Calculate Area and populate field
        area = feature.GetGeometryRef().GetArea()
        #print findex, area
        outFeat.SetField(findex, area)
        
        #Write the feature and continue loop
	outLayer.CreateFeature( outFeat )
        feature.Destroy()
        outFeat.Destroy()
        area = None
        feature = layer.GetNextFeature()     
    
    # Close out the datasources
    ds.Destroy()
    outDs.Destroy()
