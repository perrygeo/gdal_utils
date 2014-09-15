#!/usr/bin/python
'''
 Revised universal soil loss equation (RUSLE3D)
 GRASS module
 Written by Matthew Perry
 11/5/2005
'''

import os, sys

def usage():
   print '''
   Revised universal soil loss equation (RUSLE3D) for determine areas suscepible to erosion
   and annual soil loss. It is a detachment limited model assuming no deposition.
   Implemented in GRASS GIS based on tutorial by Dr. Helena Mitasova found at
   http://skagit.meas.ncsu.edu/~helena/gmslab/reports/CerlErosionTutorial/denix/denixstart.html

   Usage:
         r.rusle.py dem=raster vm=raster k=raster [r=raster OR r=number] 
                    [vmscale=number] [m=number] [n=number]
   required
   -------- 
   dem     - elevation raster map
   vm      - vegetation management factor raster (ie C & P factors)
   k       - soil erodibility raster
   
   optional
   --------
   r       - (default:50) rainfall intensity raster OR a constant value
   vmscale - (default:1)  scaling factor for VM map
   m       - (default:0.4)
   n       - (default:1.2)
             m and n are constants used in the RUSLE equation
             Lower values => dispersed flow.
             Higher values => turbulent flow. existing rills or disturbed areas.
             Ranges => m=0.4-0.6 ;  n=1-1.4.

   '''
   sys.exit(1)

#----------------------------------------------------------
# Parse input variables  
# --------------------------------------------------------
try:
   for i in len(sys.argv):
      p,v = sys.argv[i].split('=') 
   
      if p == 'elevation' or p == 'dem':
         DEM = str(v)
      if p == 'vm' or p == 'cp':
         VM = str(v)
      if p == 'k':
         K = str(v)
      if p == 'r':
         R = str(v)
      if p == 'vmscale':
         VMScale = str(v)
      if p == 'm':
         m = str(v)
      if p == 'n':
         n = str(v)
except:
   usage()

#Check for required inputs
if not DEM or not VM or not K:
   usage()

#----------------------------------------------------------
# Default constants (if not specified)
# ---------------------------------------------------------
# Average rainfall intensity, use constant if raster not specified
if not R:
   R=50.0

# Combined C and P, VM is the vegetation managment factor
# The raster has the VM value * 1000 so we have to scale accordingly
if not VMScale:
   VMScale=1

# Lower values => dispersed flow.
# Higher values => turbulent flow. existing rills or disturbed areas.
# Ranges => m=0.4-0.6 ;  n=1-1.4.
if not m:
   m=0.4
if not n:
   n=1.2

#----------------------------------------------------------
# GRASS environment
#----------------------------------------------------------
# Cell area should be cellsize * cellsize
# BUT... Minasova gives just the cellsize so we'll use that.. for now
env = os.popen('g.region -gp')
#skip the first 4 lines which are extents
for i in range(4):
   env.readline()
cellsize = float(env.readline().split('=')[1].strip())

#----------------------------------------------------------
# Processing commands
#----------------------------------------------------------
# Calculate flow accumulation from DEM
os.popen('r.flow %s dsout=flowacc' % DEM )

# Calculate Slope fro DEM
os.popen('r.slope.aspect elevation=%s slope=slope' % DEM )

# Calculate the LS factor based on slope and flow accumulation
os.popen('r.mapcalc lsfact=%f*exp(flowacc*%s/22.1,%f)*exp(sin(slope)/0.09,%f)'
          % (m+1.0, cellsize, m, n) ) 

# Calculate Soil loss
os.popen('r.mapcalc rusle=%f*%s*%s*%s*%f' % (R,K,'lsfact',VM,VMScale) )
