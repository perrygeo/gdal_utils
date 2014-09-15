###############################################################################
# interpolate.py - Interpolates a ASCII point file to a Surfer Grid
#
# David Finlayson
# Operational Geologist
# Western Coastal and Marine Geology
# US Geological Survey
# Tel: (831) 427-4757
# email: dfinlayson@usgs.gov
#
# LICENSE:
# --------
#
# I place this script in the Public Domain. However, if you find the script useful
# (or not) please send me an email.
#
# PROGRAM REQUIREMENTS:
# ---------------------
#
# The script is designed to run on a Windows XP computer with a licensed copy
# of Surfer 8 and a full installation of Python 2.4 (with the win32com extensions)
# 
# INSTRUCTIONS:
# -------------
#
# If this is the first time you have used Python to call Surfer, you will need
# to register the Surfer COM Object model with Python. The easiest way to do this
# is to launch the Pythonwin IDE (this comes with the win32com extensions) and 
# select: 
# 
# Tools > COM Makepy Utility > Surfer 8 Type Library (1.0) > OK. 
#
# The script will now run from the Windows Command Prompt (CMD.EXE).
# Try typing: 
#
# > interpolate.py -h 
#
# usage: interpolate.py [Options] InFile OutGrid
#
# Interpolates a ASCII point file to a Surfer Grid
#
# options:
#  -h, --help            show this help message and exit
#  -x NUM, --xColumn=NUM
#                        column number of easting coordinate [default: 1]
#  -y NUM, --yColumn=NUM
#                        column number of northing coordinate [default: 2]
#  -z NUM, --zColumn=NUM
#                        column number of value to grid [default: 3]
#  -m METHOD, --Method=METHOD
#                        select interpolation method from among:
#                        NearestNeighbor, Kriging or MovingAverage [default:
#                        Kriging]
#  -r RADIUS, --SearchRadius=RADIUS
#                        search ellipse radius [default: 3 m]
#  -s SPACING, --GridSpacing=SPACING
#                        Grid spacing (resolution) of output grid [default: 1
#                        m]
#  -H, --Header          input file contains one header line
#  -v, --Version         output the version number and exit [default: False]#
#
# The two required arguments are:
#
# InFile  - the name of the ascii table you wish to interpolate. InFile must be
#           in a format that Surfer can parse (for example, space delimited x y z)
# OutGrid - the binary Surfer 7 grid (format used by both Surfer 7 and 8) you 
#           wish to create
#
#
# HISTORY
# -------
#
# Version 0.6 - (December 25, 2006) Added additional documentation to the script.
# Version 0.5 - First Public Version of program.
################################################################################
import sys, os
from optparse import OptionParser

def GridExtent(Surfer, InFile, xCol, yCol, Header):
    """ extracts the region values """

    # Open the worksheet
    Worksheet = Surfer.Documents.Open(FileName=InFile)

    # Using bit flag masks we can calculate only the stats we need
    # instead of doing all of them which is time consuming
    # I looked these values up interactively from the
    # win32com.client.constants object for Surfer
    WksStatsMinimum = 32
    WksStatsMaximum = 64
    StatsToCalc = WksStatsMinimum | WksStatsMaximum

    # X column
    WksRange = Worksheet.Columns(xCol)
    Stats = WksRange.Statistics(Sample=False, Header=Header, Flags=StatsToCalc)
    xMin = Stats.GetMinimum()
    xMax = Stats.GetMaximum()

    # Y column
    WksRange = Worksheet.Columns(yCol)
    Stats = WksRange.Statistics(Sample=False, Header=Header, Flags=StatsToCalc)
    yMin = Stats.GetMinimum()
    yMax = Stats.GetMaximum()
    
    # Close document to save memory    
    Surfer.Documents.CloseAll()
    return(xMin, xMax, yMin, yMax)

def OptimalRange(RangeMin, RangeMax, GridSpacing):
    """ expands input data range to be integers evenly divisible by the resolution """
    # assume that RangeMin < RangeMax and that 
    import math
    xMin = RangeMin
    xMax = RangeMax
    
    xMin = math.floor(xMin)
    (FractionCell, WholeCells) = math.modf((xMax - xMin)/GridSpacing)
    NumCells = WholeCells + 1
    xMax = xMin + (NumCells * GridSpacing)
    return(xMin, xMax, NumCells + 1)

def GetOptionsParser():
    """ returns commandline Options """
    Usage = "usage: %prog [Options] InFile OutGrid\n\nInterpolates a ASCII point file to a Surfer Grid"
    Parser = OptionParser(usage=Usage)
    Parser.add_option("-x", "--xColumn", 
        action="store", 
        type="int", 
        dest="xCol",
        help="column number of easting coordinate [default: 1]", 
        metavar="NUM",
        default=1)
    Parser.add_option("-y", "--yColumn", 
        action="store", 
        type="int", 
        dest="yCol",
        help="column number of northing coordinate [default: 2]", 
        metavar="NUM",
        default=2)
    Parser.add_option("-z", "--zColumn", 
        action="store", 
        type="int", 
        dest="zCol",
        help="column number of value to grid [default: 3]", 
        metavar="NUM",
        default=3)
    Parser.add_option("-m", "--Method",
        action="store",
        type="choice",
        choices=["NearestNeighbor", "Kriging", "MovingAverage"],
        dest="InterpolationMethod",
        help="select interpolation method from among: NearestNeighbor, Kriging or MovingAverage [default: Kriging]",
        metavar="METHOD",
        default="Kriging")
    Parser.add_option("-r", "--SearchRadius", 
        action="store", 
        type="float", 
        dest="SearchRadius",
        help="search ellipse radius [default: 3 m]", 
        metavar="RADIUS",
        default=3.0)
    Parser.add_option("-s", "--GridSpacing", 
        action="store", 
        type="float", 
        dest="GridSpacing",
        help="Grid spacing (resolution) of output grid [default: 1 m]", 
        metavar="SPACING",
        default=1.0)
    Parser.add_option("-H", "--Header",
        action="store_true",
        dest="Header",
        help="input file contains one header line",
        default=False)
    Parser.add_option("-v", "--Version", action="store_true", dest="Version",
        help="output the version number and exit [default: False]", 
        default=False)
    return(Parser)
    
def PrintVersion():
    """ print program version information """
    print """
    interpolate.py 0.5
    
    David Finlayson, Ph.D.
    Operational Geologist
    Western Coastal and Marine Geology
    US Geological Survey
    Tel: (831) 427-4757 
    email: dfinlayson@usgs.gov
    
    Pacific Science Center
    400 Natural Bridges Drive
    Santa Cruz, CA  95060
    """
    
def Main():
    
    # Get Command line Options
    Parser = GetOptionsParser()
    (Options, Arguments) = Parser.parse_args()
    
    if Options.Version:
        PrintVersion()
        sys.exit(0)
        
    if len(Arguments) != 2:
        Parser.error("incorrect number of arguments")
    else:
        InFile = os.path.abspath(Arguments[0])
        OutGrid = os.path.abspath(Arguments[1])
        
    # Stop if the output already exists
    if os.path.exists(OutGrid):
        Parser.error("OutGrid exists! Aborting.")
        
    # Establish communication with Surfer via COM
    import win32com.client
    Surfer = win32com.client.Dispatch("Surfer.Application")

    # Calculate the data bounds
    (xMin, xMax, yMin, yMax) = GridExtent(Surfer, InFile, Options.xCol, Options.yCol, Options.Header)
    
    # Calculate the optimum resolution
    (xMin, xMax, NumCols) = OptimalRange(xMin, xMax, Options.GridSpacing)
    (yMin, yMax, NumRows) = OptimalRange(yMin, yMax, Options.GridSpacing)
    
    # Grid the data (Nearest Neighbor for regularly spaced data)
    if Options.InterpolationMethod == "NearestNeighbor":
        Surfer.GridData(DataFile=InFile,
                         xCol=Options.xCol,
                         yCol=Options.yCol,
                         zCol=Options.zCol,
                         DupMethod=win32com.client.constants.srfDupMedZ,
                         xDupTol=Options.GridSpacing,
                         yDupTol=Options.GridSpacing,
                         NumCols=NumCols,
                         NumRows=NumRows,
                         xMin=xMin,
                         xMax=xMax,
                         yMin=yMin,
                         yMax=yMax,
                         Algorithm=win32com.client.constants.srfNearestNeighbor,
                         ShowReport=False,
                         SearchEnable=True,
                         SearchRad1=Options.SearchRadius,
                         SearchRad2=Options.SearchRadius,
                         OutGrid=OutGrid)
    elif Options.InterpolationMethod == "Kriging":
        Surfer.GridData(DataFile=InFile,
                        xCol=Options.xCol,
                        yCol=Options.yCol,
                        zCol=Options.zCol,
                        DupMethod=win32com.client.constants.srfDupMedZ,
                        xDupTol=Options.GridSpacing,
                        yDupTol=Options.GridSpacing,
                        NumCols=NumCols,
                        NumRows=NumRows,
                        xMin=xMin,
                        xMax=xMax,
                        yMin=yMin,
                        yMax=yMax,
                        Algorithm=win32com.client.constants.srfKriging,
                        ShowReport=False,
                        SearchEnable=True,
                        SearchNumSectors=4,
                        SearchRad1=Options.SearchRadius,
                        SearchRad2=Options.SearchRadius,
                        SearchMinData=8,
                        SearchDataPerSect=16,
                        SearchMaxEmpty=1,
                        SearchMaxData=64,
                        KrigType=win32com.client.constants.srfKrigPoint,
                        OutGrid=OutGrid)
    elif Options.InterpolationMethod == "MovingAverage":
        Surfer.GridData(DataFile=InFile,
                        xCol=Options.xCol,
                        yCol=Options.yCol,
                        zCol=Options.zCol,
                        DupMethod=win32com.client.constants.srfDupMedZ,
                        xDupTol=Options.GridSpacing,
                        yDupTol=Options.GridSpacing,
                        NumCols=NumCols,
                        NumRows=NumRows,
                        xMin=xMin,
                        xMax=xMax,
                        yMin=yMin,
                        yMax=yMax,
                        Algorithm=win32com.client.constants.srfMovingAverage,
                        ShowReport=False,
                        SearchEnable=True,
                        SearchRad1=Options.SearchRadius,
                        SearchRad2=Options.SearchRadius,
                        SearchMinData=8,
                        OutGrid=OutGrid)
    else:
        Parser.error("(internal error) unexpected gridding method specified")
        
    # Close Surfer
    Surfer.Quit()
    del(Surfer)
    
if __name__ == '__main__':
    Main()
