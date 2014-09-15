#!/usr/bin/env python
# modified from http://www.larsen-b.com/Article/204.html

import sys
try:
    from elementtree import ElementTree
except:
    from xml.etree import ElementTree

try:
   file = sys.argv[1]
   data = open(file,'r').read()
except:
   print sys.argv[0] + " {kismet logfile}"
   sys.exit(1)


detection = ElementTree.XML(data)

# KML Header
print """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.0">
<Document>
   <name>Kismet Log </name>
      <Folder>
         <name> Kismet Log Points </name>""" 

for node in detection.getchildren():
   try:
      ssid = node.find('SSID').text
   except AttributeError:
      #hidden SSID
      ssid = "{unknown SSID}"

   bssid = node.find('BSSID').text
   ssid = ssid.replace('&','')
   channel = node.find('channel').text
   maxrate = node.find('maxrate').text 
   encryption = node.find('encryption').text

   gps = node.find('gps-info')
   lon = gps.find('max-lon').text
   lat = gps.find('max-lat').text

   print """
	<Placemark>
	  <description><![CDATA[
            <p style="font-size:8pt;font-family:monospace;">(%s , %s)</p>
           <ul>
            <li> BSSID : %s </li>
            <li> Channel : %s </li>
            <li> Max Rate : %s </li>
            <li> Encrypt : %s </li>   
            </ul>
           ]]>
          </description>
	  <name>%s</name>
	  <Point>
	    <extrude>1</extrude>
	    <altitudeMode>relativeToGround</altitudeMode>
	    <coordinates>%s,%s,0</coordinates>
	  </Point>
	</Placemark> """ % \
   (lon,lat,bssid,channel,maxrate,encryption,ssid,lon,lat)


# KML Footer
print """  </Folder>
 </Document>
</kml>"""
