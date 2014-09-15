#!/usr/bin/python
"""
  Taken from grass wiki, 
   example of grass swig interface usage from python
"""

import python_grass6 as g6lib

input = 'elevation.dem'
mapset = 'PERMANENT'

# initialize
g6lib.G_gisinit('')
infd = g6lib.G_open_cell_old(input, mapset)
cell = g6lib.G_allocate_cell_buf()

rown=0
# the API still needs error checking to be added
while 1:
    myrow = g6lib.G_get_map_row_nomask(infd, cell, rown)
    print rown,myrow[0:10]
    rown = rown+1
    if rown==476:break

g6lib.G_close_cell(infd)
g6lib.G_free(cell)
