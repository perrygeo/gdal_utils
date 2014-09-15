#!/bin/bash
basedir=/maps/data/tiger2004fe
outdir=${basedir}/shps
cd $basedir

for state in `ls -1`; do
  cd ${basedir}/${state}
  echo "Processing $state..."

  for zip in `ls -1 *.zip`; do
     echo "    Unzipping"
     prefix=`echo "$zip" | sed 's/.zip//g'`
     echo "  $state => $prefix:"
     unzip $zip -d $prefix

     echo "    Converting to SHP"
     ogr2ogr ${outdir}/${prefix}.shp ${prefix}/ CompleteChain

     echo "    Sorting by road type"
     cd $outdir
     sortshp ${prefix} ${prefix}_sorted CFCC descending

     echo "  Removing temp files"
     cd ${basedir}/${state}
     rm ${outdir}/${prefix}.*

     echo "    Creating Spatial Index"
     shptree ${outdir}/${prefix}_sorted.shp
     #shptree ${outdir}/${prefix}.shp
 done

done

echo "Done processing states !"
echo "Creating Tile Index"

find ${outdir} -name "*_sorted.shp" -print > tigerlist.txt
tile4ms tigerlist.txt ${outdir}/tiger_index
