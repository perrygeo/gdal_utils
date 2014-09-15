#!/usr/bin/python

import YahooGeocoder as y

gc = y.Geocoder()
gc.geocode( '5024 Calle Sonia', 'Santa barbara', 'CA', '93111')
print gc.getWkt()
