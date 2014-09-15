import os
#bbox = [764909,3835650,824735,3807708]
#bbox = [791749,3816461,799691,3811070]
bbox = [763981,3830432,824677,3809215]

imgul = (710560.5,3898099.5)
cellsize = 1.0
tilesize = (1000,1000)

pl_ul = ( int((imgul[0] - bbox[0]) / cellsize*-1 ), \
          int((imgul[1] - bbox[1]) / cellsize ))
pl_lr = ( int((imgul[0] - bbox[2]) / cellsize*-1), \
          int((imgul[1] - bbox[3]) / cellsize ))

count = 0
for j in range(pl_ul[1], pl_lr[1], tilesize[1]):
    for i in range(pl_ul[0], pl_lr[0], tilesize[0]):
        count += 1
        print i,j
        cmd = "mrsiddecode -i /home/perry/data/sbdata/naip/naip_1-2_1n_s_ca083_2005_3.sid -o /home/perry/Desktop/tiles/sb_%i_%i.tif -of tifg -ulxy %i %i -wh %i %i" % \
              (i,j,i,j,tilesize[0],tilesize[1])
        print count
        print "\t" , os.popen(cmd).read()
        print
        

print
print count
