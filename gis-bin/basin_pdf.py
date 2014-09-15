#!/usr/bin/env python2.3
import cgi
import os
import mapscript
import random
import sys
import psycopg

# set HOME environment variable to a directory the httpd server can write to
os.environ['HOME'] = '/var/www/tmp/'

import matplotlib
from pylab import *
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.platypus.tables import GRID_STYLE, BOX_STYLE, LIST_STYLE
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Frame, Table


# Set up postgis connection
try:
    conn = psycopg.connect('dbname=perry host=localhost user=perry')
    c = conn.cursor()
except:
    sendError("Can't Make Postgres Connection!")

####### The heart of the app... the PDF layout ########
def createPdf(basinid,basinname):
    overwrite = True

    file = '/var/www/basin_pdf/%s.pdf' % basinid
    if os.path.exists(file):
        if overwrite:
            os.remove(file)
        else:
            return basinid
    
    # Set up the Canvas
    width = 792
    height = 612
    margin = 36

    pdf = canvas.Canvas('/var/www/basin_pdf/%s.pdf' % basinid, \
                      pagesize=(width,height))

    title = "EBM Basin Summary : %s" % basinname

    # Draw the title 
    insertTitle(pdf, margin, height-margin,title)
   
    # Draw the map 
    extents = getExtents(basinid) 
    mapimg = createMap('/opt/geodev/mapserver/na_gtn.map', \
                       400, 300, \
                       extents)
    insertMap(pdf, margin, 260, 400, 300, mapimg )
    pdf.rect(margin,260,400,300)

    # Draw the veg pie chart
    vegchart = createVegChart(basinid)
    insertMap(pdf,margin,margin,200,200,vegchart )

    # Draw the Attribute List
    lst = getBasinAttributes(basinid)
    f = Frame(480,36,200,524)
    f.addFromList(lst,pdf)
    
    # Save the work
    pdf.showPage()
    pdf.save()
    return basinid

def insertTitle(c, x, y, title):
    c.drawString(x,y,title)

def insertMap(c, x, y, width, height, img):
    c.drawImage(img, x, y, width,height,mask=None)

def createMap(mapfile, x, y, extents):
    mo = mapscript.mapObj(mapfile)
    mo.selectOutputFormat('image/gif')
    scale = 2 # double the resolution
    mo.setSize(x*scale, y*scale)
    mo.resolution = 72*scale
    # Corners returned by postgis are UR,LL and
    # mapserver expects LL,UR
    #sendError(str(extents))
    b = 50000# buffer percentage
    mo.setExtent(extents[2]-b, extents[3]-b, \
                 extents[0]+b, extents[1]+b )
    im = mo.draw()
    rand = random.randint(0,1000)
    output = '/tmp/map%s.gif' % rand
    if os.path.exists(output):
        os.remove(output)
    im.save(output)
    return output

def sendPdf(basinid):
    print "Location: http://cabrillo.nceas.ucsb.edu:8080/basin_pdf/%s.pdf\n\n" % basinid 

def getExtents(basinid):
    global c     
    table = 'na_gtn'
    sql = "select box(the_geom) as box from %s where basin_id = %s" % \
           (table, basinid)
    try:
        c.execute(sql)
    except:
        sendError("postgis query failed <br/> <p> %s </p>" % sql)

    rs = c.fetchall()
    box = rs[0][0]
    extents = box.replace(")",'').replace("(",'').split(',')
    extents = map(float,extents)
    return extents
    
def createVegChart(basinid):
    global c
    table = 'na_gtn_polyview'
    attributelist = """
      igbp0 as "Water",
      igbp1 as "Evergreen Needleleaf Forest",
      igbp2 as "Evergreen Broadleaf Forest",
      igbp3 as "Needleleaf Forest",  
      igbp4 as "Deciduous Broadleaf Forest",
      igbp5 as "Mixed Forests",               
      igbp6 as "Closed Shrublands",          
      igbp7 as "Open Shrublands",        
      igbp8 as "Woody Savannas",          
      igbp9 as "Savannas",               
      igbp10 as "Grasslands",                  
      igbp11 as "Permanent Wetlands",           
      igbp12 as "Croplands",                   
      igbp13 as "Urban and Built-Up",          
      igbp14 as "Cropland/Natural Mosaic",
      igbp15 as "Snow and Ice",               
      igbp16 as "Barren or Sparsely Vegetated" 
    """

    vegcolors = {
      "Water"                       : (134,201,226) ,
      "Evergreen Needleleaf Forest" : (33,138,33) ,
      "Evergreen Broadleaf Forest"  : (49,205,49) ,
      "Needleleaf Forest"           : (154,205,49) , 
      "Deciduous Broadleaf Forest"  : (151,250,151) , 
      "Mixed Forests"               : (143,187,143) ,               
      "Closed Shrublands"           : (187,143,143) ,          
      "Open Shrublands"             : (245,222,179) ,     
      "Woody Savannas"              : (218,235,157) ,          
      "Savannas"                    : (255,214,0) ,               
      "Grasslands"                  : (239,184,102) ,                  
      "Permanent Wetlands"          : (70,130,180) ,           
      "Croplands"                   : (250,238,115) ,                   
      "Urban and Built-Up"          : (255,0,0) ,          
      "Cropland/Natural Mosaic"     : (153,147,85) ,
      "Snow and Ice"                : (255,255,255) ,               
      "Barren or Sparsely Vegetated": (190,190,189) , 
    }    

    sql = "select %s from %s where basin_id = %s" % \
           (attributelist,table, basinid)
    try:
        c.execute(sql)
    except:
        sendError("postgis query failed <br/> <p> %s </p>" % sql)

    rs = c.dictfetchall()
    basin = rs[0]
    tmpimg = '/var/www/tmp/pietest%s.png' % basinid

    matplotlib.use('Agg')
    figure(1, figsize=(4,4))
   
    keys = basin.keys()
    #keys.sort()
    labels = []
    fracs  = []
    colors = []
    explode = []
    for k in keys:
        v = basin[k]
        if v:
            labels.append(k.replace(' ','\n'))
            explode.append(0.1)
            fracs.append(v)
            colors.append( '#%02x%02x%02x' % vegcolors[k] ) 
 
    autopct = '%1.1f%%'
    #autopct = None
    labels = None
    ax = axes([0.1, 0.1, 0.9, 0.9])
    pie(fracs, explode=explode, labels=labels, autopct=autopct, \
        colors=colors, shadow=False)
    show()
    savefig(tmpimg)
    return tmpimg

def getBasinAttributes(basinid):
    global c
    table = 'na_gtn_polyview'
    attributelist = """
      sum_rusle as "Sediment - RUSLE prediction",
      sediment as "Sediment - Observed load",
      avg_k as "Average Soil Erodibility K",
      min_srtm as "Elevation Minimum",
      max_srtm as "Elevation Maximum",
      avg_srtm as "Elevation Average",
      med_srtm as "Elevation Median",
      sum_wb as "Total Waterbalance",
      sum_fertc as "Total Fertilizer",
      avg_pestc * pix_pestc as "Total Pesticide",
      avg_glac as "Percent Glaciation",
      igbp0 as "Percent Water",
      igbp1 as "Percent Evergreen Needleleaf Forest",
      igbp2 as "Percent Evergreen Broadleaf Forest",
      igbp3 as "Deciduous Needleleaf Forest",  
      igbp4 as "Percentage Deciduous Broadleaf Forest",
      igbp5 as "Percentage Mixed Forests",               
      igbp6 as "Percentage Closed Shrublands",          
      igbp7 as "Percentage Open Shrublands",        
      igbp8 as "Percentage Woody Savannas",          
      igbp9 as "Percentage Savannas",               
      igbp10 as "Percentage Grasslands",                  
      igbp11 as "Percentage Permanent Wetlands",           
      igbp12 as "Percentage Croplands",                   
      igbp13 as "Percentage Urban and Built-Up",          
      igbp14 as "Percentage Cropland/Natural Mosaic",
      igbp15 as "Percentage Snow and Ice",               
      igbp16 as "Percentage Barren or Sparsely Vegetated" 
"""
      
    sql = "select %s from %s where basin_id = %s" % \
           (attributelist,table, basinid)
    try:
        c.execute(sql)
    except:
        sendError("postgis query failed <br/> <p> %s </p>" % sql)

    rs = c.dictfetchall()
    basin = rs[0]

    rowheights = (23,)
    data = ( ('Attribute','Value'), )
    colwidths = (162, 92)
    styleSheet = getSampleStyleSheet()
    lst = []

    # Sort the dictionary alphabetically
    keys = basin.keys()
    keys.sort()

    for k in keys:
        v = basin[k]
        #for k,v in basinsort.items():
        if not v:
            data += ( (k, "None"), )
        else:
            data += ( (k, "%f" % float(v)), )
        rowheights += ( 16, )
    
    t = Table(data,colwidths,rowheights)
    t.setStyle(LIST_STYLE)
    lst.append(t)
    return lst


def sendError(text=None):
    print """Content-type: text/html\n
<h3> Error Occured </h3> """

    if text is None:
        print "You must specify a basin id ( ?basinid=001 )"
        print " and a basin name ( &name=Yukon )"""
    else:
        print text

    sys.exit(1)
    

#===========================================#
# Main
#
form = cgi.FormContentDict()

if 'basinid' not in form and 'name' not in form:
    sendError()
else:
    id = form['basinid'][0]
    name = form['name'][0]

createPdf(id,name)
sendPdf(id)
conn.close()


