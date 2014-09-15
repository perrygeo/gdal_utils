"""spark.py
A python module for generating sparklines.
Requires the Python Imaging Library 
"""

__author__ = "Joe Gregorio (joe@bitworking.org), Matthew Perry (perrygeo@gmail.com"
__copyright__ = "Copyright 2005, Joe Gregorio"
__contributors__ = ['Alan Powell, Matthew Perry']
__version__ = "0.1"
__license__ = "MIT"
__history__ = """

20070510 abstracted functions away from cgi-specific arg objects (MTP)

"""

import Image, ImageDraw

def sparkline_discrete(results, output=None, dmin=None, dmax=None, upper=None, width=2, height=14, \
                            below_color='gray', above_color='red', longlines=False):
    """The source data is a list of values between
      0 and 100 (or 'limits' if given). Values greater than 95 
      (or 'upper' if given) are displayed in red, otherwise 
      they are displayed in green"""
    gap = 4
    if longlines:
        gap = 0
    im = Image.new("RGB", (len(results)*width-1, height), 'white') 
 
    if dmin is None:
        dmin = min(results)
    if dmax is None:
        dmax = max(results)
    if upper is None:
        # defaults to the mean
        upper = sum(results) / len(results)

    if dmax < dmin:
        dmax = dmin
    zero = im.size[1] - 1
    if dmin < 0 and dmax > 0:
        zero = im.size[1] - (0 - dmin) / (float(dmax - dmin + 1) / (height - gap))
    draw = ImageDraw.Draw(im)
    for (r, i) in zip(results, range(0, len(results)*width, width)):
        color = (r >= upper) and above_color or below_color
        if r < 0:
            y_coord = im.size[1] - (r - dmin) / (float(dmax - dmin + 1) / (height - gap))
        else:
            y_coord = im.size[1] - (r - dmin) / (float(dmax - dmin + 1) / (height - gap))
        if longlines:
            draw.rectangle((i, zero, i+width-2, y_coord), fill=color)
        else:
            draw.rectangle((i, y_coord - gap, i+width-2, y_coord), fill=color)
    del draw                                                      
    if output:
        im.save(output, "PNG")
        return output
    else:
        return im

def sparkline_smooth(results, output=None, dmin=None, dmax=None, step=2, height=20, \
                          min_color='#0000FF',max_color='#00FF00', last_color='#FF0000', \
                          has_min=False, has_max=False, has_last=False):
    if dmin is None:
        dmin = min(results)
    if dmax is None:
        dmax = max(results)

    im = Image.new("RGB", ((len(results)-1)*step+4, height), 'white')
    draw = ImageDraw.Draw(im)
    coords = zip(range(1,len(results)*step+1, step),
                 [height - 3  - (y-dmin)/(float(dmax - dmin +1)/(height-4)) for y in results])
    draw.line(coords, fill="#888888")
    if has_min == True:
      min_pt = coords[results.index(min(results))]
      draw.rectangle([min_pt[0]-1, min_pt[1]-1, min_pt[0]+1, min_pt[1]+1], fill=min_color)
    if has_max == True:
      max_pt = coords[results.index(max(results))]
      draw.rectangle([max_pt[0]-1, max_pt[1]-1, max_pt[0]+1, max_pt[1]+1], fill=max_color)
    if has_last == True:
      end = coords[-1]
      draw.rectangle([end[0]-1, end[1]-1, end[0]+1, end[1]+1], fill=last_color)
    del draw 
    if output:
        im.save(output, "PNG")
        return output
    else:
        return im

if __name__ == "__main__":
    import random
    #generate sort-of-random list
    d = [x*random.random() for x in [10]*100]
    #sparkline_smooth(d,'/tmp/smooth.png')
    sparkline_smooth(d).show()
    #sparkline_discrete(d,'/tmp/discrete.png')
    #print " Take a look at /tmp/smooth.png and /tmp/discrete.png"
    
