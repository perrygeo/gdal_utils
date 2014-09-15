#!/usr/bin/env python
###############################################################################
# $Id: simplify.py,v 1.1 2005/04/09 19:57:18 sderle Exp $
#
# Project:  OGR Python samples
# Purpose:  Filter, copy, and simplify OGR layers.
# Author:   Schuyler Erle <schuyler@nocat.net>
#
###############################################################################
# Copyright (c) 2005, Frank Warmerdam <warmerdam@pobox.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###############################################################################
# 
#  $Log: simplify.py,v $
#  Revision 1.1  2005/04/09 19:57:18  sderle
#  added ogrified line simplification script
#

import ogr, os, sys

def CloneLayer ( ds, src_layer ):
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

def FilterLayer ( ds, src_layer, dest_layer, filter_func, *args ):
    if dest_layer is None:
	dest_layer = CloneLayer( ds, src_layer )

    # Extract all the geometry objects into a list
    # src_layer.ResetReading()
    feat = src_layer.GetNextFeature()
    while feat is not None:
	feat2 = ogr.Feature(feature_def = src_layer.GetLayerDefn())
	field_count = src_layer.GetLayerDefn().GetFieldCount()
	for i in range(field_count):
	    feat2.SetField( i, feat.GetField(i) )
	#print feat, feat.GetGeometryRef()
	feat2.SetGeometry( feat.GetGeometryRef() )

	filter_func( feat2, *args )

	dest_layer.CreateFeature( feat2 )
	feat2.Destroy()

	feat = src_layer.GetNextFeature()

def CopyLayer ( ds, src_layer, dest_layer = None ):
    return FilterLayer( ds, src_layer, dest_layer, lambda noop: 0 ) 

def _recursiveDouglasPeucker (pts, tol, j, k):
    keep = []

    if k <= j+1: # there is nothing to simplify
        return keep

    # degenerate case
    if pts[j].Distance(pts[k]) < tol:
	return keep

    # check for adequate approximation by segment S from v[j] to v[k]
    maxi = j	# index of vertex farthest from S
    maxd = 0	# distance squared of farthest vertex

    seg = ogr.Geometry( type = ogr.wkbLineString ) # segment from v[j] to v[k]
    seg.SetPoint( 0, pts[j].GetX(0), pts[j].GetY(0) )
    seg.SetPoint( 1, pts[k].GetX(0), pts[k].GetY(0) )

    # test each vertex v[i] for max distance from S
    for i in range(j+1, k):
        # compute distance
	dv = seg.Distance( pts[i] )

        # test with current max distance
        if dv > maxd: 
	    # v[i] is a new max vertex
	    maxi = i
	    maxd = dv

    seg.Destroy()

    if maxd > tol:         # error is worse than the tolerance
        # split the polyline at the farthest vertex from S
        keep.append( maxi ) # mark v[maxi] for the simplified polyline
        # recursively simplify the two subpolylines at v[maxi]
        keep.extend( _recursiveDouglasPeucker( pts, tol, j, maxi ) )  # v[j] to v[maxi]
        keep.extend( _recursiveDouglasPeucker( pts, tol, maxi, k ) )  # v[maxi] to v[k]

    # else the approximation is OK, so ignore intermediate vertices
    return keep

def SimplifyFeature ( feat, tolerance ):
    pts = []
    geom = feat.GetGeometryRef()
    #print geom.__dict__
    for n in range(geom.GetPointCount()):
	pt = ogr.Geometry( type = ogr.wkbPoint )
	pt.AddPoint( geom.GetX(n), geom.GetY(n) )
	pts.append(pt)

    keep = range(len(pts))
    keep.extend( _recursiveDouglasPeucker(pts, tolerance, 0, len(pts) - 1) )
    keep.sort()

    seg = ogr.Geometry( type = feat.GetGeometryRef().GetGeometryType()  ) 
    for n in keep:
	seg.AddPoint( pts[n].GetX(0), pts[n].GetY(0) )

    feat.SetGeometryDirectly( seg )

    for pt in pts:
	pt.Destroy()

def SimplifyLayer ( ds, src_layer, tolerance ):
    return FilterLayer( ds, src_layer, None, SimplifyFeature, tolerance )

if __name__ == "__main__":
    def Usage():
	print 'Usage: simplify.py tolerance infile.shp [outfile.shp]'
	print
	sys.exit(1)

    tolerance = None
    infile = None
    outfile = None

    for i in range(1, len(sys.argv)):
	arg = sys.argv[i]

	if tolerance is None:
	    tolerance = arg

	elif infile is None:
	    infile = arg

	elif outfile is None:
	    outfile = arg

	else:
	    Usage()

    if outfile is None:
	outfile = 'simplify.shp'

    if tolerance is None or infile is None:
	Usage()

    ds = ogr.Open( infile, update = 0 )
    shp_driver = ogr.GetDriverByName( 'ESRI Shapefile' )

    if os.access( outfile, os.F_OK ): 
	shp_driver.DeleteDataSource( outfile )

    shp_ds = shp_driver.CreateDataSource( outfile )
    SimplifyLayer( shp_ds, ds.GetLayer(0), tolerance )
    # CopyLayer( shp_ds, ds.GetLayer(0) works 
