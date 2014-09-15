#!/usr/bin/python
import sys
import cgi

OPENLAYERS_URL = "/openlayers/lib/OpenLayers.js"
MAPSERV_CGI_URL = "/cgi-bin/mapserv"
RENDER_METHOD = 'multi' # also 'single' which collapses all layers into single request
LAYER_TYPE = 'OpenLayers.Layer.WMS.Untiled' # tiled wms yields too many concurrent 
                                            # requests for most servers to handle

def getOpenLayersHtml(mapfile):
    try:
        import mapscript
        mo = mapscript.mapObj(mapfile)
    except:
        error(mapfile + " is not a valid mapfile")
    layerQueue = []
    
    html = """
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <style type="text/css">
        #map {
            width: 800px;
            height: 600px;
            border: 1px solid black;
        }
    </style>
    <script src="%s"></script>
    <script type="text/javascript">
        <!--
        function init(){
            var map = new OpenLayers.Map('map');

            baselayer = new OpenLayers.Layer.WMS.Untiled( "OpenLayers WMS", 
                    "http://labs.metacarta.com/wms/vmap0", {layers: 'basic'} );
            map.addLayer(baselayer);

""" % OPENLAYERS_URL
    
    for lyrnum in range(mo.numlayers):
        lyr = mo.getLayer(lyrnum)
        if lyr.isVisible() == 1:
            vis = 'true'
        else:
            vis = 'false'

        if RENDER_METHOD == 'multi':
            layerQueue.append(lyr.name)
            html += "           var %s = new %s( \"%s\",\n" % (lyr.name, LAYER_TYPE, lyr.name)
            html += "             \"%s?map=%s\",\n" % (MAPSERV_CGI_URL, mapfile)
            html += "             {layers: \"%s\", transparent: true, format: \"image/jpeg\" });\n" % lyr.name
            html += "           %s.setVisibility(%s);\n\n" % (lyr.name, vis)
        elif RENDER_METHOD == 'single':
            layerQueue.append(lyr.name)

    
    if RENDER_METHOD == 'single':
        html += "           var mapserv = new %s( \"Mapserver\",\n" % LAYER_TYPE
        html += "             \"%s?map=%s\",\n" % (MAPSERV_CGI_URL, mapfile)
        html += "             {layers: \"%s\", format: \"image/jpeg\" });\n" % ','.join(layerQueue)
        html += "           mapserv.setVisibility(true);\n\n"
        layerQueue = ['mapserv']
          
    html += "            map.addLayers([%s]);" % ','.join(layerQueue)

    html += """
            //map.addControl(new OpenLayers.Control.PanZoomBar());
            //map.addControl(new OpenLayers.Control.MouseToolbar());
            map.addControl(new OpenLayers.Control.LayerSwitcher());
            //map.addControl(new OpenLayers.Control.Permalink());
            //map.addControl(new OpenLayers.Control.Permalink($('permalink')));
            var bounds = new OpenLayers.Bounds(-45,-45, 0, 45);
            map.maxExtent = bounds;
            map.zoomToExtent( bounds )
            //if (!map.getCenter()) map.zoomToMaxExtent();
        }
        // -->
    </script>
  </head>
  <body onload="init()">
    <div id="map"></div>
  </body>
</html>
"""
    return html

form = cgi.FieldStorage() 
if form.has_key('mapfile'):
    print "Content-type: text/html\nStatus: 200 Ok\nContent: \n"
    print getOpenLayersHtml(form['mapfile'].value)
else:
    print "must specify a mapfile"
