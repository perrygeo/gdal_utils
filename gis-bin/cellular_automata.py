# With inspiration from http://www.scipy.org/Cookbook/GameOfLifeStrides
import numpy as np
import time
import os
from osgeo import gdal
from numpy.lib import stride_tricks
DRAW = True
SAVE = False
try:
    import pygame
    from pygame import surfarray
    from pygame.locals import *
except ImportError:
    print 'Error Importing Pygame/surfarray'
    DRAW = False


gdal.UseExceptions()

def get_GDT_from_dtype(dtype):
    mapping = {
        'int8': gdal.GDT_Byte,
        'int16': gdal.GDT_Int16,
        'uint16': gdal.GDT_UInt16,
        'int32': gdal.GDT_Int32,
        'float32': gdal.GDT_Float32
    }
    try:
        return mapping[str(dtype)]
    except KeyError:
        return gdal.GDT_Float32
    

class CellularAutomata:
    def __init__(self, orig, rule, geotrans):
        self.state_in = orig
        self.state_out = orig.copy()
        self.scale_img = float(np.max(orig))
        self.rule = rule
        self.geotrans = geotrans
        self.draw = DRAW
        self.save = SAVE
        self.step = 0

    def output(self, state):
        outdir = '/tmp/out/'
        imgpath = os.path.join(outdir, 'step_%s.tif' % self.step)
        print imgpath
        print state
  
        if self.draw:
            size = np.array(state.shape)*2
            scaleup = np.zeros(size,dtype=np.int32)
            scaleup[::2,::2] = state
            scaleup[1::2,::2] = state
            scaleup[:,1::2] = scaleup[:,::2]
            screen = pygame.display.set_mode(scaleup.shape[:2], 0, 32)
            surfarray.blit_array(screen, scaleup)
            pygame.display.flip()
            pygame.display.set_caption("Step %s" % self.step)
         
        if self.save:
            imgformat = "GTiff"
            driver = gdal.GetDriverByName( imgformat )
            gdt = get_GDT_from_dtype(state.dtype)
            dst_ds = driver.Create( imgpath, state.shape[1], state.shape[0], 1, gdt)
            dst_ds.SetGeoTransform( self.geotrans )
            dst_band = dst_ds.GetRasterBand(1)
            dst_band.WriteArray( state )
            dst_band.SetNoDataValue(0.0)

            if str(state.dtype).lower() in ['byte','uint16'] and imgformat == 'GTiff':
                print "Apply color ramp..."
                min_val, max_val = dst_band.ComputeRasterMinMax()
                start_color = (0,0,255,255)
                end_color = (255,0,0,255)
                ct = gdal.ColorTable()
                ct.CreateColorRamp(int(min_val),start_color,int(max_val),end_color)
                dst_band.SetColorTable(ct)

            dst_band = None
            dst_ds = None
            driver = None

    def run(self, steps):
        x = self.state_in
        y = self.state_out
        hood = (3,3)
        window_shape = (x.shape[0] - (hood[0] - 1), 
                        x.shape[1] - (hood[0] - 1))

        if self.draw:
            pygame.init()
            surfarray.use_arraytype('numpy')

        for a in range(steps):
            self.output(x)
            self.step += 1
            xx = stride_tricks.as_strided(x, 
                    shape=(window_shape[0], window_shape[1], hood[0], hood[1]), 
                    strides=x.strides + x.strides)

            for i in range(window_shape[0]):
                for j in range(window_shape[1]):
                    y[i+1,j+1] = self.rule(xx[i,j])

            x = y.copy()
        self.output(x)
        if self.draw:
            print "Done.. "
            time.sleep(1)
            #print "Done.. press 'q' to quit"
            #while 1:
            #    e = pygame.event.wait()
            #    if e.type == KEYDOWN and e.key == K_q: 
            #        break
            pygame.quit()


if __name__ == "__main__":

    import random
    def simple_rule(win):
        """
        Rule must return a single scalar value for each neighborhood window
        Randomly takes min or max
        """
        c = random.choice(['min','max'])
        if c == 'max':
            return np.max(win)
        else:
            return np.min(win)

    size = 128
    #start = np.array(np.random.randint(0,255,size*size).reshape([size,size]), dtype=np.int32)
    start = np.arange(size*size).reshape([size,size])
    geotrans = [ 444720, 30, 0, 3751320, 0, -30 ]

    ca = CellularAutomata(start, simple_rule, geotrans) 
    ca.run(200)
