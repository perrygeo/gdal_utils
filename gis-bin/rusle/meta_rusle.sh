#!/bin/bash

cd /home/perry

# Requires 6.1 after 11/15/05 ish when r.resamp.rst was fixed
g.region rast=dem
nsres=`g.region -g | grep 'nsres=' | sed s/nsres=//`
ewres=`g.region -g | grep 'ewres=' | sed s/ewres=//`
#g.region rast=mfi
#r.resamp.rst input=mfi ew_res=${ewres} ns_res=${nsres} elev=mfi_rst

# grow mfi or mask it - no need since the rst step extrapolates 

# Make sure all null values are truly set to null - no need since grids have this info 

# Recalculate dem to true elevations
#g.region rast=dem
#r.mapcalc "dem_real=dem-1000"

# grow the elevation data out by 2 cells, but assign each new cell a value of zero.
# This makes sure all on-land slope values are valid.
#r.grow input=dem_real output=dem_grow radius=2.01 new=0

# reclass igbp
#cat tables/igbp.colors | r.colors map=igbp color=rules
cat tables/igbp_vm_2.reclass | r.reclass input=igbp output=vm2 

# reclass soils
#cat tables/soils_k_1.reclass | r.reclass input=soil output=k1

# instead of r.flow
#r.terraflow.short elev=dem_grow filled=dem_fill direction=dem_dir swatershed=dem_swshd accumulation=flowacc tci=dem_tci

# run rusle since 'flowacc' exists, it will use the terraflow version rather than try f.flow
scalefactor=`echo "scale=12;0.0010000*0.0100000* 0.0002471*${nsres}*${ewres}*0.9071847/17.02" | bc`
scripts/r.rusle.py dem=dem_grow vm=vm2 k=k1 r=mfi_rst scale=${scalefactor} output=rusle2
