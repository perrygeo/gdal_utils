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
   RUSLE3D
   ---------------------------------------------------------------------------
   Revised universal soil loss equation (RUSLE3D) for determine areas
   suscepible to erosion and annual soil loss. It is a detachment
   limited model assuming no deposition. Implemented in GRASS GIS based
   on tutorial by Dr. Helena Mitasova found at
   http://skagit.meas.ncsu.edu/~helena/gmslab/reports/CerlErosionTutorial/denix/denixstart.html

   Usage:
         r.rusle.py dem=raster vm=raster k=raster output=raster 
          [r=raster OR r=number] [scale=number] [m=number] [n=number]

   required
   -------- 
   dem     - digital elevation model  (meters)
   vm      - vegetation management factor raster (ie C & P factors)
   k       - soil erodibility raster
   output  - name of output rusle map
   
   optional
   --------
   r       - (default:50) rainfall intensity raster OR a constant value
   scale   - (default:1)  combined scaling factor for VM and K maps
   m       - (default:0.4)
   n       - (default:1.2)
             m and n are constants used in the RUSLE equation
             Lower values => dispersed flow.
             Higher values => turbulent flow. existing rills or disturbed areas.
             Ranges => m=0.4-0.6 ;  n=1-1.4.

   '''
   sys.exit(1)

def mapExists(map):
    rastlist = os.popen('g.list rast')
    found = 0
    for i in list:
        if i.find(map) != -1:
            found = 1
    if found = 1:
        return True
    else
        return False 
    


#----------------------------------------------------------
# Default constants (if not specified)
# ---------------------------------------------------------
dem = None
vm = None
k = None
output = None

# Average rainfall intensity, use constant if raster not specified
r=50.0

# Combined C and P, VM is the vegetation managment factor
# The raster has the VM value * 1000 so we have to scale accordingly
# Also soil K values can be scaled so this represents a combined scale factor
#  Scale = VMScale * KScale
scale=1

# Lower values => dispersed flow.
# Higher values => turbulent flow. existing rills or disturbed areas.
# Ranges => m=0.4-0.6 ;  n=1-1.4.
m=0.4
n=1.2

#----------------------------------------------------------
# Parse input variables  
# --------------------------------------------------------
go = 1
if go == 1:
   for i in range(len(sys.argv)):
      p = sys.argv[i].split('=') 

      if p[0] == 'dem':
         dem = str(p[1])
      if p[0] == 'vm' or p[0] == 'cp':
         vm = str(p[1])
      if p[0] == 'k':
         k = str(p[1])
      if p[0] == 'output':
         output = str(p[1])
      if p[0] == 'r':
         r = str(p[1])
      if p[0] == 'scale':
         scale = float(p[1])
      if p[0] == 'm':
         m = str(p[1])
      if p[0] == 'n':
         n = str(p[1])

#Check for required inputs
if not dem or not vm or not k or not output:
   usage()

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
if not mapExists(flowacc):
    os.popen('r.flow %s dsout=flowacc' % dem )

# Calculate Slope fro DEM
# TBD : If slope already exists, skip
if not mapExists(flowacc):
    os.popen('r.slope.aspect elevation=%s slope=slope' % dem )

# Calculate the LS factor based on slope and flow accumulation
# TBD : If lsfact already exists, skip
if not mapExists(flowacc):
    os.popen('r.mapcalc "lsfact=%f*exp(flowacc*%s/22.1,%f)*exp(sin(slope)/0.09,%f)"'
          % (m+1.0, cellsize*cellsize, m, n) )

# Calculate Soil loss
os.popen('r.mapcalc %s=%s*%s*%s*%s*%f' % (output,r,k,'lsfact',vm,scale) )
