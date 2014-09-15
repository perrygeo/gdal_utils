import os

DEM = "lidar1_fill"
RASTER_WSHD = "watersheds"
BMPS = "bmp.csv"
BMPOUT = "bmpout.csv"
OUTSHPDIR = "shps"

def getElev(x, y, dem):
    cmd = "r.what input=%s cache=500 null=* east_north=%s,%s" % (dem, x, y)
    out = os.popen(cmd).read()
    elevation = float(out.split("|")[3])
    return elevation

def createPourRast(x,y):
    os.popen("g.remove rast=lake,baselake")
    cmd = "echo \"%s,%s,1\" | r.in.xyz input=- output=lake method=mean type=CELL fs=, x=1 y=2 z=3 percent=100" % (x,y)
    out = os.popen(cmd).read()
    os.popen("g.copy rast=lake,baselake")
    return 

def iterLake(dem, target_vol, pour_elev):
    volume = 0
    step = 1
    level = pour_elev        
    while volume < target_vol:
        level += step
        cmd = "r.lake -o dem=%s wl=%s seed=lake" % (dem, level)
        print cmd
        print volume
        volume = float(os.popen(cmd).read())    
    return (level-pour_elev, volume) 

def lake(dem, pour_elev):
    cmd = "r.lake -o dem=%s wl=%s seed=baselake" % (dem, pour_elev)
    volume = float(os.popen(cmd).read())    
    return volume

def createSafeDEM(dem, wshd_id):
    os.popen("g.remove rast=safedem")
    os.popen("g.region rast=%s" % dem)

    # safedem = create a wsdh masked dem    
    cmd = "r.mapcalc 'safedem = if(%s == %s, %s, null())'" % (RASTER_WSHD, wshd_id, dem)          
    os.popen(cmd)
    os.popen("g.region rast=safedem")
    return

def readBMPs(infile):
    fh = open(infile, 'r')
    cont = fh.readlines()
    bmps = [x.split(",") for x in cont]
    fh.close()
    return bmps

def outputShapefiles(id):
    layers = ["lake", "baselake"]
    for layer in layers:
        os.popen("g.remove vect=zzzlake_vector" )
        os.popen("g.remove rast=zzzlake")
        cmd = "r.mapcalc 'zzzlake = if(isnull(%s), null(), %s)'" % (layer,id)
        os.popen(cmd)
        cmd = "r.to.vect input=zzzlake output=zzzlake_vector feature=area"
        os.popen(cmd)
        cmd = "v.out.ogr input=zzzlake_vector type=area dsn=%s olayer=%s_%s format=ESRI_Shapefile" % (OUTSHPDIR, layer, id) 
        os.popen(cmd)
    return

if __name__ == "__main__":
    outfh = open(BMPOUT,'w')
    bmps = readBMPs(BMPS)
    outfh.write("id,height,volume,6ftvolume\n")
    for bmp in bmps:
        try:
            id = bmp[0]
            x = float(bmp[1])
            y = float(bmp[2])
            target_vol = float(bmp[3])
        except:
            continue
        pour_elev = getElev(x,y,DEM)
        createPourRast(x,y)
        createSafeDEM(DEM, id)
        (height, volume) = iterLake("safedem", target_vol, pour_elev)
        vol6ft = lake("safedem",pour_elev + 6)    
        outfh.write( ",".join(str(x) for x in [id,height,volume,vol6ft]))
        outfh.write("\n")
        outfh.flush()
        outputShapefiles(id)        
    outfh.close() 

    
    
