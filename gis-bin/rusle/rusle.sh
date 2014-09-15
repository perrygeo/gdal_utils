#!/bin/bash

# Input Rasters
# --------------------------------------------------------
DEM="elevation.dem"
VM="landcover.C4"
K="soils.Kfactor"

# append this prefix to all output rasters
prefix="rusle_"

# Input constants
# ---------------------------------------------------------
# Average rainfall intensity
R="50."
# Combined C and P, VM is the vegeation managment factor
# The raster has the VM value * 1000 so we have to scale accordingly
VMScale="0.001"

# Lower values => dispersed flow. 
# Higher values => turbulent flow. existing rills or disturbed areas.
# m=0.4-0.6 
m="0.4"
# this is simply m + 1 ... 
# why do it as a string.. because bash can't do anything but integer math without a struggle 
mplus="1.4"
# n=1-1.4.
n="1.1"

# Cell area should be cellsize * cellsize
# BUT... Minasova gives just the cellsize so we'll use that.. for now
cellarea="30.0"

# Processing commands
#----------------------------------------------------------
# Calculate flow accumulation from DEM
r.flow ${DEM} dsout=${prefix}flowacc

# Calculate Slope fro DEM
r.slope.aspect elevation=${DEM} slope=${prefix}slope

# Calculate the LS factor based on slope and flow accumulation
r.mapcalc "${prefix}lsfact=${mplus}*exp(${prefix}flowacc*${cellarea}/22.1,${m})*exp(sin(${prefix}slope)/0.09,${n})"
LS=${prefix}lsfact

# Calculate Soil loss
r.mapcalc "${prefix}soilloss=${R}*${K}*${VM}*${LS}*${VMScale}"

