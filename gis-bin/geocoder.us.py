#!/usr/bin/python
import xmlrpclib
import sys

def usage():
  print " usage: python geocode.py address"

def getArgs(args):
    address = None

    for i in range(1, len(sys.argv)):
	arg = sys.argv[i]

	if address is None:
	    address = arg
	else:
	    usage()
     
    if (address):
        return address  
    else:
        usage() 
        sys.exit(1)

def geocode(address):
    p = xmlrpclib.ServerProxy('http://rpc.geocoder.us/service/xmlrpc')
    r = p.geocode(address)
    return r[0];

if __name__ == "__main__":
    address = getArgs(sys.argv)
    r = geocode(address)
    print "--------------"
    print "Address:"
    print '  ', r['number'], r['prefix'], r['street'], r['suffix'], r['type']
    print '  ', r['city'], r['state'], r['zip']
    print "Coordinates:" 
    print '  ', r['long'], r['lat']
    print "--------------"


