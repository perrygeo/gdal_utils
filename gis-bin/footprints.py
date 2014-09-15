# raster_footprints.py
# Credits to Sean Gillies
# http://zcologia.com/news/16
#
# Create footprint shapefile
import ogr

driver = ogr.GetDriverByName('ESRI Shapefile')
footprints_shp = driver.CreateDataSource('index/')
footprints = footprints_shp.CreateLayer('footprints',
                 geom_type=ogr.wkbPolygon)
fd = ogr.FieldDefn('FILENAME', ogr.OFTString)
fd.SetWidth(30)
footprints.CreateField(fd)

# Loop over a number of georeferenced images
import glob
import gdal

files = glob.glob('*.tif')
for file in files:
    # Get georeferencing and size of imagery
    dataset = gdal.Open(file)
    g = dataset.GetGeoTransform()
    pixels = dataset.RasterXSize
    lines = dataset.RasterYSize
    minx = g[0]
    maxx = minx + pixels * g[1]
    maxy = g[3]
    miny = maxy + lines * g[5]
    
    # append to the 'footprints' layer
    wkt = 'POLYGON ((%f %f, %f %f, %f %f, %f %f, %f %f))' \
        % (minx, miny, minx, maxy, maxx, maxy, maxx, miny, minx, miny)
    g = ogr.CreateGeometryFromWkt(wkt)
    f = ogr.Feature(feature_def=footprints.GetLayerDefn())
    f.SetField(0, file)
    f.SetGeometryDirectly(g)
    footprints.CreateFeature(f)
    f.Destroy()

# destroy footprints_shp to flush and close
footprints_shp.Destroy()
