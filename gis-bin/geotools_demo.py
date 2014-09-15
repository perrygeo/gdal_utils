#!/usr/local/bin/jython
import sys
import os
from org.geotools.data import DataStore, DataStoreFinder
from org.geotools.data.shapefile import *
from org.geotools.feature import *
import com.vividsolutions.jts.geom.Geometry
from java.util import HashMap, Map
from java import net

def info(dspath):

    # get datastore
    shp = "file://%s" % os.path.abspath(dspath)
    params = HashMap()
    params.put('url',net.URL(shp))
    dataStore = DataStoreFinder.getDataStore(params)

    typeName = dataStore.getTypeNames()[0]
    featureSource = dataStore.getFeatureSource(typeName)
    featureCollection = featureSource.getFeatures()
    featureType = featureSource.getSchema()

    # Print out feature source info (ie layer info)
    #'getBounds', 'getClass', 'getCount', 'getDataStore'
    print "Datastore         : ", featureSource.getDataStore()
    print "Layer Name        : ", typeName
    print "Number of features: ", featureCollection.count
    print "Bounding Box      : ", featureSource.getBounds()
    
    # Print out feature attribute types
    for atype in featureType.getAttributeTypes():
        print atype.getName(), atype.getType()



    return None

    f_iter = featureCollection.iterator()
    while f_iter.hasNext():
        feat = f_iter.next()
        print "==============" ,feat.getID()
        for i in range(feat.getNumberOfAttributes()):
            print "\t %s " % feat.getAttribute(i)

    featureCollection.close(f_iter)
        
if __name__ == "__main__":
    if len(sys.argv) > 1:
        info(sys.argv[1])
    else:
        print "jython geotools_demo.py <dataset>"

