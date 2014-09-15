#!/usr/bin/python
import sys, re, xml.sax
from xml.sax.handler import ContentHandler
from cElementTree import Element, SubElement, ElementTree

exportTags = ["name", "class", "highway", "oneway", "surface", "lanes"]
exportWays = 1 
segments = {}
class osm2gml (ContentHandler):
    def __init__ (self, fh):
        ContentHandler.__init__(self)
        self.fh = fh

    def startDocument (self):
        self.node = {}
        self.fields = {}
        self.current = None

    def startElement (self, name, attr):
        if name == 'node':
            self.node[attr["id"]] = (attr["lon"], attr["lat"])
        elif name == 'segment':
            from_node = self.node[attr["from"]]
            to_node   = self.node[attr["to"]]
            self.current = [ [from_node, to_node], {"id": attr["id"]} ]
	    if (exportWays):
	        segments[attr['id']] = [from_node, to_node] 
        elif name == 'tag' and self.current:
            try:
	    	self.current[-1][attr["k"].replace(":","_").replace(" ","_")] = attr["v"]
            except:
	    	self.current[attr["k"].replace(":", "_").replace(" ","_")] = attr["v"]
	    self.fields[attr["k"]] = True
        elif name == 'way' and exportWays:
            self.current = {'id': attr["id"], 'segments': []}
        elif name =='seg' and self.current:
            if segments.has_key(attr["id"]):
	    	self.current['segments'].append(segments[attr["id"]])
            
    def endElement (self, name):
        if name == 'segment':
            self.generateSegment(*self.current)
            self.current = None
        elif name == 'way' and exportWays:
	    segments = self.current['segments']
	    self.current['segments'] = sort_segments(self.current['segments'])	
            if (self.current['segments']): 
	    	self.generateWay(self.current)
	    else:
	        self.current['segments'] = segments
	        self.generateMultiWay(self.current)
            self.current = None
    
    def generateMultiWay (self, attr):
        featureMember = Element("gml:featureMember")
        feature = SubElement(featureMember, "way")
        FID = SubElement(feature, "FID")
        FID.text = str(attr["id"])
        geometryProperty = SubElement(feature, "gml:geometryProperty")
        lineString = SubElement(geometryProperty, "gml:MultiLineString")
	data = []
	for i in attr['segments']:
	     lsm = SubElement(lineString, "gml:lineStringMember")
             ls = SubElement(lsm, "gml:LineString")
             coordinates = SubElement(ls, "gml:coordinates")
	     coordinates.text = " ".join(map(lambda x: "%s,%s" % x, i))
	for k, v in attr.iteritems():
	    if k != "segments":
            	SubElement(feature, "" + k).text = v
        ElementTree(featureMember).write(self.fh, "utf-8")
        self.fh.write("\n")
    def generateWay (self, attr):
        featureMember = Element("gml:featureMember")
        feature = SubElement(featureMember, "way")
        FID = SubElement(feature, "FID")
        FID.text = str(attr["id"])
        geometryProperty = SubElement(feature, "gml:geometryProperty")
        lineString = SubElement(geometryProperty, "gml:LineString")
        coordinates = SubElement(lineString, "gml:coordinates")
	coordinates.text = " ".join(map(lambda x: "%s,%s" % x, attr['segments']))
        for k, v in attr.iteritems():
	    if k != "segments":
            	SubElement(feature, "" + k).text = v
        ElementTree(featureMember).write(self.fh, "utf-8")
        self.fh.write("\n")

    def generateSegment (self, coords, attr):
        featureMember = Element("gml:featureMember")
        feature = SubElement(featureMember, "segment")
        feature.set("gml:fid", str(attr["id"]))
        FID = SubElement(feature, "FID")
        FID.text = str(attr["id"])
        geometryProperty = SubElement(feature, "gml:geometryProperty")
        lineString = SubElement(geometryProperty, "gml:LineString")
        coordinates = SubElement(lineString, "gml:coordinates")
        coordinates.text = " ".join(map(lambda x: "%s,%s" % x, coords))
        for k, v in attr.iteritems():
            if k in exportTags:
                SubElement(feature, "" + k).text = v
        ElementTree(featureMember).write(self.fh, "utf-8")
        self.fh.write("\n")
def sort_segments (segments):
    ordered = list(segments)
    ordered.sort(lambda x, y: cmp(x[1], y[1]) or
                  cmp(x[0], y[0]))

    broken = 0
    max = len(ordered) * len(ordered)
    if not ordered: return []
    chain = [ordered.pop()]
    i = 0
    while ordered and i < max:
        item = ordered.pop()
        if item[1][1] == chain[0][0][1] \
           and item[1][0] == chain[0][0][0]:
           chain.insert(0, item)
        elif item[0][1] == chain[-1][1][1] \
           and item[0][0] == chain[-1][1][0]:
           chain.append(item)
        elif item[0][1] == chain[-1][0][1]\
           and item[0][0] == chain[-1][0][0]:
           chain.append([item[1], item[0]])
        elif item[1][1] == chain[-1][1][1]\
           and item[1][0] == chain[-1][1][0]:
           chain.append([item[1], item[0]])
        else:
           ordered.insert(0, item)
        i+=1
    if i == max:
	return []
    else:
    	polyline = []
    	for i in chain:
    	    polyline.append(i[0])
	polyline.append(chain[-1][1])
	return polyline

if __name__ == "__main__":
    osmParser = osm2gml(sys.stdout)
    print '<?xml version="1.0"?>'
    print '<gml:FeatureCollection xmlns:gml="http://www.opengis.net/gml"'
    print '    xmlns="http://www.openstreetmap.org/gml/">'
    xml.sax.parse( sys.stdin, osmParser )
    print '</gml:FeatureCollection>'
