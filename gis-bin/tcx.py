#!/usr/bin/python
"""
Author: Matthew Perry
Description:
Date: 

Copyright 2008 Matthew T. Perry
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at 
   http://www.apache.org/licenses/LICENSE-2.0 
Unless required by applicable law or agreed to in writing, software 
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and 
limitations under the License.
"""

def parse_tcx3(infile):
    from BeautifulSoup import BeautifulStoneSoup as bss
    soup = bss(open(infile,'r'))
    
    ###### Activity
    for activity in soup.findAll('activity'):
        sport = activity['sport']
        activityid = activity.id.string

        ###### Lap
        for lap in activity.findAll('lap'):
            lapid = lap['starttime']
            time = time_code(lapid)
            totaltime = float(lap.totaltimeseconds.string)
            distance = float(lap.distancemeters.string)
            maxspeed = float(lap.maximumspeed.string)
            calories = float(lap.calories.string)
            intensity = lap.intensity.string
            cadence = float(lap.cadence.string)
            trigger = lap.triggermethod.string

            try: avghr = float(lap.averageheartratebpm.value.string)
            except: avghr = None

            try: maxhr = float(lap.maximumheartratebpm.value.string)
            except: maxhr = None
            
            ##### Track
            for track in lap.findAll('track'):

                ##### Trackpoint
                for point in track.findAll('trackpoint'):
                    pointid = point.time.string
                    print pointid
                    time = time_code(pointid)
                    cumdist = float(point.distancemeters.string)

                    try:
                        coords = [float(x) for x in 
                                 [point.position.longitudedegrees.string, 
                                  point.position.latitudedegrees.string]]
                    except: coords = None

                    try: cadence = int(point.cadence.string)
                    except: cadence = None

                    try: alt = float(point.altitudemeters.string)
                    except: alt = None

                    try: hr = int(point.heartratebpm.value.string)
                    except: hr = None



def time_code(t): 
    '''Parse a time & return seconds from epoch'''
    import time
    y = int(t[:4])
    m = int(t[5:7])
    day = int(t[8:10])
    h = int(t[11:13])
    minute = int(t[14:16])
    sec = int(t[17:19])
    timestamp = y,m,day,h,minute,sec,-1, -1, -1
    timeCode = time.mktime(timestamp)
    return timeCode

if __name__ == "__main__":
    import sys
    infile = sys.argv[1] #"/home/perry/data/garmin/2008-08-17T15:01:30Z.tcx"
    tcx = parse_tcx3(infile)
    

