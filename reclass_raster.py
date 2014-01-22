#!/usr/bin/env python
###############################################################################
# reclass_raster.py
#
# Purpose:  Convert raster of continuous values into discrete categories
# Auther:   Matthew Perry, perrygeo@gmail.com
#
###############################################################################
# Copyright (c) 2011, Matthew Perry
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
# 
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
###############################################################################
import sys
import numpy
from osgeo import gdal
from progressbar import ProgressBar, Percentage, ETA, SimpleProgress

def parse_config(fh):
    lines = fh.readlines()
    cfg = []
    for line in lines:
        items = [float(x) for x in line.strip().split(',')]
        items[2] == int(items[2])
        if len(items) == 3:
            cfg.append(items)
        else:
            raise Exception

    if len(cfg) < 1:
        raise Exception
    return cfg

def classify_val(val, cfg):
    for rule in cfg:
        if val >= rule[0] and val < rule[1]:
            return rule[2]
    print "WARNING: value %s did not fall into any class"
    return None
    
if __name__ == '__main__':
    format = 'GTiff'

    gdal.AllRegister()
    argv = gdal.GeneralCmdLineProcessor( sys.argv )
    if len(argv) < 4:
        print "python reclass_raster.py input.tif classes.cfg output.tif"
        print "where classes.cfg contains lines like:"
        print "min,max,class"
        sys.exit( 0 )

    cont = gdal.Open( argv[1], gdal.GA_ReadOnly )
    if cont is None: 
        print "%s is not a valid raster file" % argv[1]
        sys.exit( 0 )

    try:
        cfg_fh = open(argv[2], 'r')
        cfg = parse_config(cfg_fh) 
    except:
        print "Configuration file '%s' is not valid" % argv[4]
        sys.exit( 0 )

    geotransform = cont.GetGeoTransform()
    xsize = cont.RasterXSize
    ysize = cont.RasterYSize
    projection = cont.GetProjection()
    if projection == '':
        projection = None
    
    # Create output
    driver = gdal.GetDriverByName(format)
    if driver is None:
        print 'Format driver %s not found, pick a supported driver.' % format
        sys.exit( 1 )

    bands = 1
    band_type = gdal.GDT_Int16
    out = driver.Create( argv[3], xsize, ysize, bands, band_type )
    if out is None:
        print 'Creation failed, terminating.'
        sys.exit( 1 )
        
    out.SetGeoTransform(geotransform)
    if projection:
        out.SetProjection(projection)

    inband = cont.GetRasterBand(1)
    indata = inband.ReadAsArray()

    outband = out.GetRasterBand(1) 

    progress = ProgressBar(widgets=['Processed Lines ', SimpleProgress(), ' (', Percentage(), ') ' , ETA(), ' remaining' ],maxval=ysize)
    progress.start()
    progress.update_interval = 1
    progress.next_update = 1

    for line in range(ysize):
        zones_line = []
        for xpos in range(xsize):
            val = indata[line, xpos]
            zone = classify_val(val, cfg)
            zones_line.append(zone)
        outband.WriteArray( numpy.array([zones_line]), 0, line )   
        progress.update(line)

    print 
