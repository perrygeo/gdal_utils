#!/usr/bin/env python
"""
shapefile to virtual earth
a completely standalone html generator for generating a web map based on a
set of points
"""
try:
    from osgeo import ogr
except ImportError:
    import ogr

import sys

template = """<html>
<body style="background-color:black">

<!-- HTML Map element - the size must be specified here, or in the CSS -->
<center><div id="mapstraction" style="border: 2px white solid; margin-top: 15px; width: 950px; height: 700px;color:white;">Loading Map</div></center>

<script type="text/javascript" src="http://mapstraction.com/svn/source/mapstraction.js"></script>


<!--------------- CHOOSE YOUR MAP PROVIDER ------------>
%s

<script type="text/javascript">
// initialise the map with your choice of API
%s

<!------------ END MAP PROVIDER SPECIFIC CODE ----------->

// create a lat/lon object and display the map centered on a latitude and longitude (Google zoom levels)
var lat = %s;
var lon = %s;
var myPoint = new LatLonPoint( lat, lon ); 
mapstraction.setCenterAndZoom(myPoint, 2);

mapstraction.addControls({
    pan: true, 
    zoom: 'large',
    overview: true,
    map_type: true

});

mapstraction.addMapTypeControls();

var points = [ 
%s     
];

for (var i=0; i<points.length; i++) {
    // create a marker positioned at a lat/lon 
    pt = new LatLonPoint(points[i]['lat'], points[i]['lon']);
    my_marker = new Marker(pt);
    //my_marker.setIcon('./img/icon.gif'); // 
    %s
    my_marker.setInfoBubble(points[i]['info']);
    mapstraction.addMarker(my_marker);
}

</script> 
     
</body>
</html>
"""

feature_template = '{"lat": %f, "lon":%f, "label":"%s", "info":"%s"}'



def shp2mapstraction(shp, out, labelatt, provider):

    if provider.lower() == "ms":
        provider_js = "<script src=\"http://dev.virtualearth.net/mapcontrol/v3/mapcontrol.js\"></script>"
        provider_init = "var mapstraction = new Mapstraction('mapstraction','microsoft');"                                                                                     
    elif provider.lower() == "yahoo":
        provider_js = "<script type=\"text/javascript\" src=\"http://api.maps.yahoo.com/ajaxymap?v=3.0&appid=MapstractionDemo\"></script>"
        provider_init = "var mapstraction = new Mapstraction('mapstraction','yahoo');"
    elif provider.lower() == "openlayers":
        provider_js = "<script src=\"http://openlayers.org/api/OpenLayers.js\"></script>" 
        provider_init = "var mapstraction = new Mapstraction('mapstraction','openlayers');"       
    else:
        print "Choose either Yahoo, OpenLayers or MS as the map service provider"
        sys.exit(1)

    ds = ogr.Open(shp)
    layer = ds.GetLayer(0)
    geomtype = layer.GetLayerDefn().GetGeomType()
    if geomtype != ogr.wkbPoint and geomtype != ogr.wkbPoint25D:
        print " That's not a point shapefile. Thanks for trying. Please play again."
        sys.exit(1)

    ext = layer.GetExtent()
    (clon, clat) = ( (ext[0] + ext[1])/2. , (ext[2] + ext[3])/2. )
    
    fc = layer.GetFeatureCount()
    jsfeatures = []
    for i in range(fc):
        f = layer.GetFeature(i)
        g = f.GetGeometryRef()

        
        if labelatt:
            fidx = f.GetFieldIndex(labelatt)
            label = f.GetFieldAsString(fidx)
        else:
            label = "point %d" % i
            
        fcount = f.GetFieldCount()
        info = "<table>"
        for j in range(fcount):
            fname = f.GetDefnRef().GetFieldDefn(j).GetName()
            val = f.GetFieldAsString(j)
            info += "<tr><th align='left'>%s</th><td>%s </td></tr>" % (fname, val)

        info += "</table>";     
        jf = (g.GetY(), g.GetX(), label , info  )
        jsfeatures.append(jf)
 
    points = ", ".join( [feature_template % x for x in jsfeatures])

    # should we display labels or not? 
    if labelatt:
        jslabel = "my_marker.setLabel(points[i]['label']);"
    else:
        jslabel = "//my_marker.setLabel(points[i]['label']);"
        
    html = template % (provider_js, provider_init, clat, clon, points, jslabel)
    fh = open(out,"w")
    fh.write(html)
    fh.close()
    return True
         
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print "shp2Mapstraction.py <point shapefile> <output html> <provider - Yahoo|MS|OpenLayers> {label attribute}"
        sys.exit(1)

    shp = sys.argv[1]
    outfile = sys.argv[2]
    prov_string = sys.argv[3]

    labelattrib = None
    if len(sys.argv) >= 5:
        labelattrib = sys.argv[4]
    
    shp2mapstraction(shp, outfile, labelattrib, prov_string)
