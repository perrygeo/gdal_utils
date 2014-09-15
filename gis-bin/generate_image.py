#!/usr/bin/python
#
# Generates a single large PNG image for a UK bounding box
# Tweak the lat/lon bounding box (ll) and image dimensions
# to get an image of arbitrary size.
#
# To use this script you must first have installed mapnik
# and imported a planet file into a Postgres DB using
# osm2pgsql.
#
# Note that mapnik renders data differently depending on
# the size of image. More detail appears as the image size
# increases but note that the text is rendered at a constant
# pixel size so will appear smaller on a large image.

from mapnik import *

if __name__ == "__main__":
    mapfile = "/home/perry/src/perrygeo/mapserver/osm-local.xml"
    tile_uri = "/home/perry/Desktop/osm_image.png"
    ll = (-119.945,34.375,-119.555,34.546)
    z = 16
    imgx = 700 * z
    imgy = 400 * z

    m = Map(imgx,imgy)
    load_map(m,mapfile)
    prj = Projection("+proj=merc +datum=WGS84")
    c0 = prj.forward(Coord(ll[0],ll[1]))
    c1 = prj.forward(Coord(ll[2],ll[3]))
    bbox = Envelope(c0.x,c0.y,c1.x,c1.y)
    #bbox = Envelope(ll[0],ll[1],ll[2],ll[3])
    m.zoom_to_box(bbox)
    im = Image(imgx,imgy)
    render(m, im)
    view = im.view(0,0,imgx,imgy) # x,y,width,height
    save_to_file(tile_uri,'png',view)
