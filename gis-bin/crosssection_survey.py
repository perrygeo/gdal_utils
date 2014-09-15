#!/usr/bin/python
"""
Author: Matthew Perry
Description:
Date: 

Copyright 2008 Matthew T. Perry
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
from osgeo import ogr
from osgeo import gdal
import math

def calc_perp_angles(a):
    left = a - 90
    right = a + 90
    if left < 0: 
        left = 360 + left
    if right > 360:
        right = right - 360
    return (left,right)

def polar_to_cartesian(a, r):
    theta = a * math.pi/180.
    x = r * math.sin(theta)
    y = r * math.cos(theta)
    # these forumla's differ from many texts since 
    # our 0 degree mark is actuall north (axes are swapped)
    return (x,y)

def arange(start, stop=None, step=None):
    if stop is None:
        stop = float(start)
        start = 0.0
    if step is None:
        step = 1.0
    cur = float(start)
    while cur < stop:
        yield cur
        cur += step

class XSecSurvey():
    def __init__(self, id, x, y, a, w, numsteps=10):
        self.id = id 
        self.x = float(x)
        self.y = float(y)
        self.downangle = float(a)
        self.width = float(w)
        self.perpangles = calc_perp_angles(float(a))
        self.xsecpts = []
        self.step = self.width/numsteps
        rr = arange(self.width/-2, (self.width/2) + self.step, self.step) 
        dist = 0 
        for r in rr:
            cart = polar_to_cartesian(self.perpangles[1], r)
            self.xsecpts.append( (self.x + cart[0],
                                  self.y + cart[1],
                                  dist))
            dist += self.step
                                  


def parse_input(infile):
    surveys = []
    fh = open(infile,'r')
    lines = fh.readlines()
    fh.close()
    for l in lines[1:]:
        c = l.split(',')
        surveys.append( XSecSurvey(c[0],c[1],c[2],c[3],c[4]) )
    return surveys
        

def calc_transects(infile, demfile, outdir):
    surveys = parse_input(infile)
    demds = gdal.Open(demfile)
    dem = demds.GetRasterBand(1) 
    gt = demds.GetGeoTransform()

    for s in surveys:
        pts = []
        for p in s.xsecpts:
            pts.append( (p[2], getRasterValue(p[0],p[1],dem,gt)) )

        fh = open(outdir+"X"+s.id+".DAT", 'w')
        fh.write("""*** Stability Analysis
Boeing SSFL 
Junction: ---
Cross Section %s
*** Slope   No.   Active Channel
   -.--     %s    --     --   
*** Station (ft)
%s
*** Elevation (ft)
%s
*** Roughness Coefficient
---------
*** Critical Shear strees (lb/ft2)    D50 (ft)
 ----                                 ----
*** D85  D60  D50  D30  D15  D10
    --   --   --   --   --   --
*** Mass fraction (total must equal 100)
*** D85  D60  D50  D30  D15  D10
    --   --   --   --   --   --
*** Sand fraction (decimal fraction)
    ---
***
END
""" % (s.id, 
       len(s.xsecpts), 
       ' '.join(str(x[0]) for x in pts),
       ' '.join(str(round(x[1],1)) for x in pts),
       ))

        fh.close()

             

       

def getRasterValue(x,y,band,gt):
    xoff = int((x - gt[0]) / gt[1])  
    yoff = int((y - gt[3]) / gt[5]) 
    try:
        a = band.ReadAsArray( xoff, yoff, 1, 1)
        return a[0][0]        
    except:
        return 0

    

if __name__ == "__main__":
    infile = "/home/perry/Desktop/xsec/pts.csv"
    demfile = "/home/perry/Desktop/xsec/dem.img"
    outdir = "/home/perry/Desktop/xsec/"
    calc_transects(infile, demfile, outdir) 
    

