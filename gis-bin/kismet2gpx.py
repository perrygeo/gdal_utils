#!/usr/bin/python
import sys, time, re, xml.sax
from xml.sax.handler import ContentHandler

class kismet2gpx (ContentHandler):
    def __init__ (self):
        ContentHandler.__init__(self)

    def startElement (self, name, attr):
        if name == "gps-point" and attr['bssid'] == "GP:SD:TR:AC:KL:OG":
            print """<trkpt lat="%s" lon="%s">
            <ele>%s</ele>
            <time>%s</time>
            </trkpt>""" % (attr['lat'], attr['lon'], attr['alt'], time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(float(attr['time-sec']))))
            

if __name__ == "__main__":
    kismetParser = kismet2gpx()
    print """<?xml version="1.0"?>
    <gpx
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="http://www.topografix.com/GPX/1/0"
    >
    <trk><trkseg>
    """
    xml.sax.parse( sys.stdin, kismetParser )
    print """</trkseg></trk></gpx>"""
