#!/usr/bin/env python
###############################################################################
# classify_terrain.py
#
# Purpose:  Module to classify terrain based on slope, aspect and DEM rasters
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
"""
Assume you have 3 rasters, dem, slope (in degrees) and aspect, from which the terrain classification maps will be derived.

- Create a configuration file to define the classifications of terrain zones. 
This file is a comma-separated value (CSV) text file with the following structure:

    minimum elevation, minimum aspect*, maximum aspect*, minimum slope

* the min/max aspect assume that we are going clockwise and that North is equal to both 0 and 360 
(likewise East = 90, South = 180, West = 270). For example, in order to capture everything from 
NW to NE including N, you would need to define the "minimum" aspect as 315 and the "maximum" as 45.

An example configuration would be as follows; 
We want to create a zone above 1400 meters, 
between NW-NE aspect and >= 30 degree slopes, this would be the line in the csv file

    1400, 315, 45, 30

There will be one line in the csv per defined zone. 
If there is overlap between the zone definitions, the first matching line would take precedence; 
the order of lines in the csv file DOES matter! For example, in the following configuration file:

    1400, 315, 45, 30
    1800, 315, 45, 35

If a pixel was 1850m, north facing with a 36 degree slope, 
it would be classified into zone 1 even though it matches the criteria of zone 2 as well.

- Using the classify_terrain.py script, you would run the model by the following syntax:

    python classify_terrain.py <dem> <aspect> <slope> <configuration> <ouput tif>

For example:

    python classify_terrain.py dem.tif aspect.tif slope.tif config.csv terrain_zones.tif

The output terrain_zones.tif file will have pixel values of 0 when the pixel does not match ANY 
of the zone criteria. If it matches, the output pixel value will be the appropriate category number. 
"""
import sys
import numpy
from osgeo import gdal
from progressbar import ProgressBar, Percentage, ETA, SimpleProgress

USAGE = """
    python create_terrain.py <dem> <aspect> <slope> <configuration> <ouput tif>

    An example configuration would be as follows; 
    We want to create a "Yellow" zone above 1400 meters, 
    between NW-NE aspect and >= 30 degree slopes, this would be the line in the csv file

        1400, 315, 45, 30
"""

NO_ZONE = 0

class Zone:
    def __repr__(self):
        return 'Zone %s: (elevation > %s, aspect %s to %s, slope > %d)' % \
                (self.id, self.minelev, self.minaspect,
                self.maxaspect, self.minslope)

    def __init__(self, id, items):
        self.id = id
        if len(items) == 4:
            self.minelev = items[0]
            self.minaspect = items[1]
            self.maxaspect = items[2]
            self.minslope = items[3]
        else:
            raise Exception

def classify_zone(elev, aspect, slope, cfg):
    for zone in cfg:
        if slope >= zone.minslope and elev >= zone.minelev:
            if zone.maxaspect < zone.minaspect: 
                # includes N
                if (aspect >= zone.minaspect and aspect <= 360.) or \
                   (aspect <= zone.maxaspect and aspect >= 0.0):
                    return zone.id
            else:
                # doesn't include N
                if aspect >= zone.minaspect and aspect <= zone.maxaspect:
                    return zone.id

    return NO_ZONE


def parse_config(fh):
    lines = fh.readlines()
    cfg = []
    id = 1
    for line in lines:
        items = [int(x) for x in line.split(',')]
        if len(items) == 4:
            cfg.append(Zone(id, items))
        else:
            raise Exception
        id += 1
    if len(cfg) < 1:
        raise Exception
    return cfg


if __name__ == '__main__':
    format = 'GTiff'
    dem = None
    aspect = None
    slope = None
    cfg = None

    gdal.AllRegister()
    argv = gdal.GeneralCmdLineProcessor( sys.argv )
    if len(argv) < 6:
        print USAGE
        sys.exit( 0 )

    dem = gdal.Open( argv[1], gdal.GA_ReadOnly )
    aspect = gdal.Open( argv[2], gdal.GA_ReadOnly )
    slope = gdal.Open( argv[3], gdal.GA_ReadOnly )
    if dem is None: 
        print "DEM %s is not a valid raster file" % argv[1]
        sys.exit( 0 )
    if aspect is None: 
        print "Aspect '%s' is not a valid raster file" % argv[2]
        sys.exit( 0 )
    if slope is None: 
        print "Slope '%s' is not a valid raster file" % argv[3]
        sys.exit( 0 )

    try:
        cfg_fh = open(argv[4], 'r')
        cfg = parse_config(cfg_fh) 
    except:
        print "Configuration file '%s' is not valid" % argv[4]
        sys.exit( 0 )

    for z in cfg:
        print z

    geotransform = dem.GetGeoTransform()
    xsize = dem.RasterXSize
    ysize = dem.RasterYSize
    projection = dem.GetProjection()
    if projection == '':
        projection = None
    
    # Confirm the same extents and sizes
    for fh in [slope, aspect]:
        try:
            assert geotransform == fh.GetGeoTransform()
            assert xsize == fh.RasterXSize
            assert ysize == fh.RasterYSize
        except:
            print "Slope, Aspect and DEM must have the same dimensions!!"
            sys.exit(1)

    # Create output
    driver = gdal.GetDriverByName(format)
    if driver is None:
        print 'Format driver %s not found, pick a supported driver.' % format
        sys.exit( 1 )

    bands = 1
    band_type = gdal.GDT_Int16
    out = driver.Create( argv[5], xsize, ysize, bands, band_type )
    if out is None:
        print 'Creation failed, terminating.'
        sys.exit( 1 )
        
    out.SetGeoTransform(geotransform)
    if projection:
        out.SetProjection(projection)

    # Go line-by-line through 3 inputs, match to Zones and output line
    demband = dem.GetRasterBand(1)
    aspectband = aspect.GetRasterBand(1)
    slopeband = slope.GetRasterBand(1)
    outband = out.GetRasterBand(1) 
  
    demdata = demband.ReadAsArray()
    aspectdata = aspectband.ReadAsArray()
    slopedata = slopeband.ReadAsArray()

    progress = ProgressBar(widgets=['Processed Lines ', SimpleProgress(), ' (', Percentage(), ') ' , ETA(), ' remaining' ],maxval=ysize)
    progress.start()
    progress.update_interval = 1
    progress.next_update = 1

    for line in range(ysize):
        zones_line = []
        for xpos in range(xsize):
            elev = demdata[line,xpos]
            aspect = aspectdata[line,xpos]
            slope = slopedata[line,xpos]
            zone = classify_zone(elev, aspect, slope, cfg)
            zones_line.append(zone)
        outband.WriteArray( numpy.array([zones_line]), 0, line )   
        progress.update(line)

    dem = None
    aspect = None
    slope = None
    out = None
    print 
    print " Terrain classification model complete at %s" % argv[5]
