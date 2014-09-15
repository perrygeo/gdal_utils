#!/usr/bin/python
# vmap_convert.py
# Converts VMAP-0 data layers into Shapefiles
# scw 1.13.2005
 
# still need to add a lookup table of datasets => SQL to grab a particular dataset.
 
import os
import sys

ogrPath = "/opt/fwtools/bin_safe/"

def usage():
    print
    print 'vmap_convert.py'
    print 'Extracts a vector dataset from VMAP-0 data, merges into a global shapefile'
    print 'Usage: vmap_convert.py VMAP-directory VMAP-layer outfile.shp <where> '
    print 'Example : vmap_convert.py /data/vmap/ polbnda@bnd(*)_area political_merged.shp \'use=26\''
    print 'Notes : '
    print '  - VMAP directory MUST be the full path to the directory containing the VMAP folers.'
    print '    These subfolders are: v0eur, v0noa, v0sas, v0soa.'
    print '  - output file must be shapefile (with the .shp extension)'
    print '  - the optional <where> parameter is used to extract a subset of the data.'
    print '  - All data will be exported as NAD83, the VMAP default.'
    print 'Author: Shaun C. Walbridge 1.13.2006 <scw@scisland.com>'
    print 
    sys.exit(1)

def error(message):
    print
    print message
    print
    sys.exit(1)

def getArgs(args):
    vmapDir        = None
    vmapLayer      = None
    outFile        = None
    whereClause    = None
    formatSupport  = None
    arg            = []
     
    if len(args) == 1:
        usage()
             
    for i in range(1, len(args)):
        arg.append(args[i])

    vmapDir   = arg[0]
    vmapLayer = arg[1]
    outFile   = arg[2]

    vmapDir = os.path.abspath(vmapDir)
    
    if not (os.path.exists(vmapDir)):
        error('The directory "' + vmapDir + '"does not exist')

    if os.path.exists(outFile):
        error('The output file "' + outFile +'" already exists. Pick a different name.')
    
    try:
        whereClause = arg[3]
    except:
        print "No query given, extracting entire dataset."
     
    formats = os.popen(ogrPath + "ogrinfo --formats").readlines()
    
    for i in formats:
        if (i.find('OGDI') != -1):
            formatSupport = True

    if formatSupport is None:
        error('The OGDI Driver could not be found.  Install FWTools and try again.')
   
    if (vmapDir is not None and vmapLayer is not None and outFile is not None):
        return vmapDir, vmapLayer, outFile, whereClause
    else:
        usage()    

if __name__ == "__main__":

    vmapDir, vmapLayer, outFile, whereClause = getArgs(sys.argv);

    vmapAreas  = { 'v0eur' : 'eurnasia', 
                   'v0noa' : 'noamer',   
                   'v0sas' : 'sasaus',  
                   'v0soa' : 'soamafr' }
    shapeParts = ['dbf', 'shx', 'shp', 'prj']               
    outPrefix  = outFile.split('.')[0] # the filename sans extension
    vmapPass = 0

    for k, v in vmapAreas.iteritems():
        vmapPass += 1
        glPath   = 'gltp:/vrf' + vmapDir + '/' + k + '/vmaplv0/' + v
        areaName = k + '_' + outPrefix
            
        print "Converting %s layer %s ..." % (k, vmapLayer), 
        if whereClause is not None:
            ogrCommand = '%s/ogr2ogr %s.shp %s \'%s\' -where \'%s\'' \
                          % (ogrPath,areaName, glPath, vmapLayer, whereClause)
        else:
            ogrCommand = '%s/ogr2ogr %s.shp %s \'%s\'' % (ogrPath, areaName, glPath, vmapLayer)

        #print ogrCommand
        os.system(ogrCommand)
        
        print "merging...",

        # if we're processing the first dataset, seed the merge with the data instead of copying into
        if (vmapPass == 1):
            ogrCommand = '%s/ogr2ogr %s.shp %s.shp' % (ogrPath, outPrefix, areaName)
        else:
            ogrCommand = '%s/ogr2ogr -update -append %s.shp %s.shp -nln %s %s' \
                                      % (ogrPath, outPrefix, areaName, outPrefix, areaName)
        #print ogrCommand
        os.system(ogrCommand)

        for i in range(len(shapeParts)):
            delFile = '%s.%s' % (areaName, shapeParts[i])

            if os.path.exists(delFile):
                os.remove(delFile)
        print "done."

    print "Output written to %s" % (outFile)
