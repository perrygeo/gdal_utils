#!/bin/bash

# Input Rasters
# --------------------------------------------------------
DEM="elevation.dem"
VM="landcover.C5"
K="soils.Kfactor"

# append this prefix to all output rasters
prefix="usped_"

# Input constants
# ---------------------------------------------------------
# Average rainfall intensity
R="50."
# Combined C and P, VM is the vegeation managment factor
# The raster has the VM value * 1000 so we have to scale accordingly
VMScale="0.001"


# Cell area should be cellsize * cellsize
# BUT... Minasova gives just the cellsize so we'll use that.. for now
cellarea="30.0"

# Processing commands
#----------------------------------------------------------
# Calculate flow accumulation from DEM
r.flow ${DEM} dsout=${prefix}flowacc

# Calculate Slope fro DEM
r.slope.aspect elevation=${DEM} slope=${prefix}slope aspect=${prefix}aspect

# (prevailing rills)

# m=1.6 n=1.3 for rill
m="1.6"
n="1.3"
r.mapcalc "${prefix}rill_sflowtopo=exp(${prefix}flowacc*${cellarea},${m})*exp(sin(${prefix}slope),${n})" 
r.mapcalc "${prefix}rill_qsx=${R}*${K}*${VM}*${VMScale}*${prefix}rill_sflowtopo*cos(${prefix}aspect)"
r.mapcalc "${prefix}rill_qsy=${R}*${K}*${VM}*${VMScale}*${prefix}rill_sflowtopo*sin(${prefix}aspect)"
r.slope.aspect ${prefix}rill_qsx dx=${prefix}rill_qsx.dx
r.slope.aspect ${prefix}rill_qsy dy=${prefix}rill_qsy.dy
r.mapcalc "${prefix}rill_erdep=${prefix}rill_qsx.dx+${prefix}rill_qsy.dy"

# (prevailing sheet)

# m=n=1 for sheet so we don't use the exponents
r.mapcalc "${prefix}sheet_sflowtopo=${prefix}flowacc*${cellarea}*sin(${prefix}slope)" 
r.mapcalc "${prefix}sheet_qsx=${R}*${K}*${VM}*${VMScale}*${prefix}sheet_sflowtopo*cos(${prefix}aspect)"
r.mapcalc "${prefix}sheet_qsy=${R}*${K}*${VM}*${VMScale}*${prefix}sheet_sflowtopo*sin(${prefix}aspect)"
r.slope.aspect ${prefix}sheet_qsx dx=${prefix}sheet_qsx.dx
r.slope.aspect ${prefix}sheet_qsy dy=${prefix}sheet_qsy.dy
r.mapcalc "${prefix}sheet_erdep=10*(${prefix}sheet_qsx.dx+${prefix}sheet_qsy.dy)"
