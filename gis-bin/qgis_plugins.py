#!/usr/bin/env python
"""
qgis_plugins.py

Allows you to inspect available Quantum GIS python plugins from 
repository and install them to local qgis. 

Usage:
 qgis_plugins.py list 
 qgis_plugins.py install Geocoder

author: Matthew Perry
license: BSD
date: 2007-Oct-13

TODO:
- automatic discovery of python plugin dir
- error checking
- test on windows
- handle permissions gracefully 
- make a gui plugin based on this
"""
import urllib
import sys
import os
import tempfile
import zipfile
from xml.dom import minidom, Node

###############  
REPOS_LISTING = "http://spatialserver.net/cgi-bin/pyqgis_plugin.rb"
PYPLUGIN_DIR = "/usr/local/share/qgis/python/plugins" 
###############


class unzip:
    """ unzip.py
    Version: 1.1

    Extract a zipfile to the directory provided
    It first creates the directory structure to house the files
    then it extracts the files to it.

    import unzip
    un = unzip.unzip()
    un.extract(r'c:\testfile.zip', 'c:\testoutput')
    

    By Doug Tolton (http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/252508)
    """
    def __init__(self, verbose = True, percent = 10):
        self.verbose = verbose
        self.percent = percent
        
    def extract(self, file, directory):
        if not os.path.exists(directory):
            os.mkdir(directory)

        zf = zipfile.ZipFile(file)

        # create directory structure to house files
        self._createstructure(file, directory)

        num_files = len(zf.namelist())
        percent = self.percent
        divisions = 100 / percent
        perc = int(num_files / divisions)

        # extract files to directory structure
        for i, name in enumerate(zf.namelist()):

            if self.verbose == True:
                print "Extracting %s" % name
            elif perc > 0 and (i % perc) == 0 and i > 0:
                complete = int (i / perc) * percent
                print "%s%% complete" % complete

            #if not name.endswith('/'):
            if not name[len(name)-1] == '/':
                outfile = open(os.path.join(directory, name), 'wb')
                outfile.write(zf.read(name))
                outfile.flush()
                outfile.close()


    def _createstructure(self, file, directory):
        self._makedirs(self._listdirs(file), directory)


    def _makedirs(self, directories, basedir):
        """ Create any directories that don't currently exist """
        for directory in directories:
            print basedir, directory
            curdir = os.path.join(basedir, directory)
            if not os.path.exists(curdir):
                os.mkdir(curdir)

    def _listdirs(self, file):
        """ Grabs all the directories in the zip structure
        This is necessary to create the structure before trying
        to extract the file to it. """
        zf = zipfile.ZipFile(file)

        dirs = []

        for name in zf.namelist():
            #if name.endswith('/'):
            if name[len(name)-1] == '/':
                dirs.append(name)

        dirs.sort()
        return dirs



def retrieve_list():
    repos = urllib.urlopen(REPOS_LISTING).read()
    repos_xml = minidom.parseString(repos)
    plugin_nodes = repos_xml.getElementsByTagName("pyqgis_plugin")
    plugins = [ 
      {"name"    : x.getAttribute("name").encode(),
       "version" : x.getAttribute("version").encode(),
       "desc"    : x.getElementsByTagName("description")[0].childNodes[0].nodeValue.encode(),
       "author"  : x.getElementsByTagName("author_name")[0].childNodes[0].nodeValue.encode(),
       "url"     : x.getElementsByTagName("download_url")[0].childNodes[0].nodeValue.encode(),
       "filename": x.getElementsByTagName("file_name")[0].childNodes[0].nodeValue.encode()}
       for x in plugin_nodes]
     
    return plugins

def usage():
    print
    print "qgis_plugins.py list  - lists the available plugins"
    print "qgis_plugins.py install <plugin_name> - gets and installs the plugin"
    print
    return None

def install_plugin(plugin):
    plugin_list = retrieve_list()
    target = [x for x in plugin_list if x["name"] == plugin]
    if target:
        # Take the first match
        target = target[0]
        url = target["url"]
        filename = target["filename"]

        print "Retrieving from %s" % url
        try:
            tmpdir = tempfile.gettempdir()
            outfile = os.path.join(tmpdir,filename)
            urllib.urlretrieve(url,outfile)          
        except:
            print "Failed to download file to %s" % outfile
            sys.exit(1)

        print "Extracting to plugin directory (%s)" % PYPLUGIN_DIR
        try:
            un = unzip()
            un.extract(outfile, PYPLUGIN_DIR)        
        except:
            print "Failed to unzip file to %s ... check permissions" % PYPLUGIN_DIR
            sys.exit(1)

        print "Python plugin installed. Go to Plugins > Plugin Manager to enable %s." % plugin
     
    else:
        print "No plugins found named %s" % plugin

    return

        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    elif sys.argv[1] == "list":
        list = retrieve_list()
        print "\nQGIS python plugins avialable from \n%s" % REPOS_LISTING
        print "------------- "
        for p in list:
            print "%s ( version %s )" % (p["name"], p["version"])
            print "\t%s by %s" % (p["desc"],p["author"])
        print

    elif sys.argv[1] == "install":
        print "Preparing to install %s ... " % sys.argv[2]
        install_plugin(sys.argv[2])  
    
    else:
        usage()

