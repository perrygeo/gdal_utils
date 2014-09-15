# ---------------------------------------------------------------------------
# dasym_tables.py
# Created on: Wed Jan 11 2006 
# Written by: Matthew Perry
# Usage: See the "script arguments" section
# ---------------------------------------------------------------------------

#================================================================#
# Prepare Environment

# Import system modules
import sys, string, os, win32com.client

# Create the Geoprocessor object
gp = win32com.client.Dispatch("esriGeoprocessing.GpDispatch.1")

# Set the necessary product code
gp.SetProduct("ArcInfo")

# Check out any necessary licenses
gp.CheckOutExtension("spatial")

# Load required toolboxes...
gp.AddToolbox("C:/Program Files/ArcGIS/ArcToolbox/Toolboxes/Spatial Analyst Tools.tbx")
gp.AddToolbox("C:/Program Files/ArcGIS/ArcToolbox/Toolboxes/Conversion Tools.tbx")
gp.AddToolbox("C:/Program Files/ArcGIS/ArcToolbox/Toolboxes/Data Management Tools.tbx")


#----------------------------------------#
# Script Arguments

Temp_Workspace                           = "C:\\WorkSpace\\temp"

try:
    #INPUTS
    Spatial_Units_Raster                 = sys.argv[1] # raster containing country code
    Attribute_Lookup_Table               = sys.argv[2] # dbf containing countries and all attributes of interest
    Attribute_Lookupt_Table_Join_Item    = sys.argv[3] # country code
    Attribute_Lookup_Table_Value_Item    = sys.argv[4] # the variable of interest
    Aux_Raster                           = sys.argv[5] # landcover
    Weighting_Table                      = sys.argv[6] # Table relating land cover classes to relative weights
    Weighting_Table_Join_Field           = sys.argv[7] # column with landcover codes
    Weighting_Table_Weight_Field         = sys.argv[8] # column with relative wieghts
    #OUTPUTS
    Combined_Raster                      = sys.argv[9] # output of aml, input to gp script
    Combined_Raster_Table                = sys.argv[10] # output of aml, input to gp script
    Output_Raster                        = sys.argv[11] # the dasymetric map
except:
    #INPUTS
    Spatial_Units_Raster                 = "C:\\WorkSpace\\FAO\\dasym\\units\\units_as"
    Attribute_Lookup_Table               = "C:\\WorkSpace\\FAO\\dasym\\lookups\\faocia.dbf"
    Attribute_Lookupt_Table_Join_Item    = "CODE" 
    Attribute_Lookup_Table_Value_Item    = "FERT" 
    Aux_Raster                           = "C:\\WorkSpace\\clipped_rusle_inputs\\as_igbp"
    Weighting_Table                      = "C:\\WorkSpace\\FAO\\dasym\\weights\\C.dbf" 
    Weighting_Table_Join_Field           = "LANDCOVER"
    Weighting_Table_Weight_Field         = "WEIGHT"

    #OUTPUTS
    Combined_Raster                      = Temp_Workspace + "\\ctpc"
    Combined_Raster_Table                = Temp_Workspace + "\\ctpc.dbf" 
    Output_Raster                        = "C:\\WorkSpace\\FAO\\dasym\\outputs\\as_fertC"

#--------------------------------#
# Constants
Joined_Output_Table_Name                 = "combine_weight_join"
Joined_Output_Table                      = Temp_Workspace + "\\" + Joined_Output_Table_Name + ".dbf"
Combine_Reclass                          = Temp_Workspace + "\\combine2_rcl"
Temp_Raster                              = Temp_Workspace + "\\temp_dasy"
Combined_Raster_Table_Variable_Field     = "VOI" # Should be constant


#================================================================#
# Main

#---------------------------------#
# Call the AML as the first step
#  b/c ArcGIS can't handle raster attribute tables
amlPath = os.path.dirname(sys.argv[0]) + "\\"
sCommandLine  = "arc.exe \"&run\" \"" + amlPath + "dasym_combine.aml \" "
sCommandLine += Spatial_Units_Raster + " " + Attribute_Lookup_Table + " "
sCommandLine += Attribute_Lookupt_Table_Join_Item + " " + Attribute_Lookup_Table_Value_Item + " "
sCommandLine += Aux_Raster + " "
sCommandLine += Combined_Raster + " " + Combined_Raster_Table + " " + Temp_Workspace + "'"
os.system(sCommandLine)

# gp.AddMessage(" ****** Combined Layers")
print " ****** Combined Layers"

#------------------------------------------------#
# Determine the column names based on user input
   
base = os.path.basename(Combined_Raster_Table)
split = base.split(".")
combinedPrefix = split[0]

base = os.path.basename(Weighting_Table)
split = base.split(".")
weightedPrefix = split[0]

base = os.path.basename(Aux_Raster)
split = base.split(".")
auxprefix = split[0]
auxprefix = auxprefix[:10]

Variable_Field = combinedPrefix + "_VOI" # "ctfc_VOI"  # Combined_Raster_Table _ VOI
Variable_Field = Variable_Field[:10]
Weight_Field   = weightedPrefix + "_" + Weighting_Table_Weight_Field # "TFC_WEIGHT"
Weight_Field   = Weight_Field[:10]
Count_Field    = combinedPrefix + "_COUNT"   # Combined_Raster_Table _ COUNT
Count_Field    = Count_Field[:10]
Value_Field    = combinedPrefix + "_VALUE"   # Combined_Raster_Table _ VALU
Value_Field    = Value_Field[:10]

Combined_Raster_Table_Join_Field  = auxprefix.upper() # "LANDCOVER2" # Name of aux raster truncated and caps
    
try:    
    #------------------------------------------------#
    # Join Tables and create new output table    
    gp.MakeTableView_management(Combined_Raster_Table, "ctable")
    gp.AddJoin_management("ctable", Combined_Raster_Table_Join_Field, Weighting_Table, Weighting_Table_Join_Field, "KEEP_ALL") 
    gp.TableToTable_conversion("ctable", Temp_Workspace, Joined_Output_Table_Name)

    print " ****** Created joined table"

    #------------------------------------------------#
    # Add fields
    gp.AddField_management(Joined_Output_Table, "totalpc", "DOUBLE", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
    gp.AddField_management(Joined_Output_Table, "valuepp", "LONG", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
    gp.MakeTableView_management(Joined_Output_Table, "jtable")
    
    print " ****** Added Fields and reloaded table view"

    #------------------------------------------------#
    # Calculate Total of Variable Per Auxillary Data Class
    gp.CalculateField_management("jtable", "totalpc", "[" + Variable_Field + "] * [" + Weight_Field + "]")

    # Calculate Value of variable per pixel    
    gp.CalculateField_management("jtable", "valuepp", "int( [totalpc] * 10000.0 / [" + Count_Field + "]) ")

    print " ****** Calculated New Fields"
    
    #------------------------------------------------#
    # Reclass by Table...
    gp.ReclassByTable_sa(Combined_Raster, "jtable", Value_Field , Value_Field, "valuepp", Temp_Raster , "DATA")

    print " ****** Reclassed Raster"
    
    #------------------------------------------------#
    # Scale Raster to original units 
    Map_Algebra_expression = Temp_Raster + " / 10000.0"
    gp.SingleOutputMapAlgebra_sa(Map_Algebra_expression, Output_Raster)
    
    print " ****** Scaled raster"

except:
    print gp.GetMessages()
    sys.exit(1)
