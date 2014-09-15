#!/usr/bin/python
""" 
  Python Class to interface with the Yahoo Geocoder
  http://developer.yahoo.com/maps/rest/V1/geocode.html
  
  Command line usage:

    python YahooGeocoder.py '1234 My Street Name, My Town, NY, 98765'   

  Usage in a python application:

    import YahooGeocoder as y
    gc = y.Geocoder() 
    gc.geocode('1234 My Street Name, My Town, NY, 98765')
    print gc.lat, gc.lon

  Date: 09/25/2006

  Copyright 2006 Matthew T. Perry 

  Licensed under the Apache License, Version 2.0 (the "License"); 
  you may not use this file except in compliance with the License. 
  You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0 

  Unless required by applicable law or agreed to in writing, software 
  distributed under the License is distributed on an "AS IS" BASIS, 
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
  See the License for the specific language governing permissions and 
  limitations under the License.
  
"""

import sys
import urllib
from xml.dom import minidom

class Geocoder:

    def __init__(self,appid='YahooDemo'):
        self.appid = appid
        self.baseurl = "http://api.local.yahoo.com/MapsService/V1/geocode?appid=%s" % self.appid 
 
    def geocode(self,street,city=None,state=None,zip=None):

        # If everything is specified, do an exact search
        # otherwise treat the street parameter as a freeform location search
        if (city is not None and state is not None and zip is not None):
            self.request_street = urllib.quote_plus(street)
            self.request_city = urllib.quote_plus(city)
            self.request_state = urllib.quote_plus(state)
            self.request_zip = urllib.quote_plus(zip)
            self.request_url = "%s&city=%s&state=%s&zip=%s&street=%s" % \
                (self.baseurl, self.request_city, self.request_state, 
                 self.request_zip, self.request_street) 
        else:
            self.request_location = urllib.quote_plus(street)
            self.request_url = "%s&location=%s" % (self.baseurl, self.request_location) 

        self.response = urllib.urlopen(self.request_url).read().replace('\n','')
        print self.response

        self.tree = minidom.parseString(self.response)
        self.result_node = self.tree.getElementsByTagName('ResultSet')[0].getElementsByTagName('Result')[0]
        self.precision = self.result_node.getAttribute('precision')
        try:
            self.warning = self.result_node.getAttribute('warning')
        except:
            self.warning = None
        self.lon = float(self.result_node.getElementsByTagName('Longitude')[0].firstChild.nodeValue)
        self.lat = float(self.result_node.getElementsByTagName('Latitude')[0].firstChild.nodeValue)
        self.address = self.result_node.getElementsByTagName('Address')[0].firstChild.nodeValue
        self.city = self.result_node.getElementsByTagName('City')[0].firstChild.nodeValue
        self.state = self.result_node.getElementsByTagName('State')[0].firstChild.nodeValue
        self.zip_plus4 = self.result_node.getElementsByTagName('Zip')[0].firstChild.nodeValue
        self.zip = self.zip_plus4.split('-')[0]
        self.country = self.result_node.getElementsByTagName('Country')[0].firstChild.nodeValue
        self.valid = True

    def niceResponse(self):
        if self.valid is True:
            res = '\n'
            if self.warning:
                res += ' %s \n' % self.warning 

            res += " %s , %s, %s, %s, %s \n Geocoded at '%s' precision \n longitude: %s \n latitude: %s \n" % \
                  (self.address, self.city, self.state, self.zip_plus4, self.country,
                   self.precision, self.lon, self.lat)
        else:
            res = "\n Invalid query \n"

        return res
        
    def getWkt(self):
        if self.valid:
            wkt = "POINT(%f %f)" % (self.lon,self.lat)
            return wkt
    
    def test(self):
        print "works"

         
if __name__ == '__main__':

    #try:
    #    location = sys.argv[1]
    #except:
    #    print " usage: YahooGeocoder.py 'street,city,state,zip' "
    #    sys.exit(1)

    #gc = Geocoder()
    #gc.geocode(location)
    #print gc.niceResponse()
   # 
    #import YahooGeocoder as y

    gc = Geocoder()
    gc.geocode( '5024 Calle Sonia', 'Santa barbara', 'CA', '93111')
    print gc.getWkt()
