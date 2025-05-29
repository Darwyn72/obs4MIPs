# Modified 25-05-15 by PS for testing with ESMValTool processed dataset SAGE-CCI-OMPS+
# See RC #457 

import pandas as pd
import netCDF4 as nc
from netCDF4 import Dataset 
import cmor
import xarray as xr
from xarray.coding.times import encode_cf_datetime
import numpy as np
import cftime
import sys,os,glob

#%% User provided input 
cmorTable = '/Users/paul.smith/demo/Tables/obs4MIPs_Amon.json' ; # Aday,Amon,Lmon,Omon,SImon,fx

#EXAMPLES with command line input
# python -i runCMOR_ESMVAlTool-obs.py 

# python -i runCMOR_ESMVAlTool-obs.py rlut CALIPSO-ICECLOUD_input.json /p/user_pub/PCMDIobs/obs4MIPs_input/ESMValTool/ESACCI-CLOUD/cli_mon_CALIPSO-ICECLOUD-1-00_DLR_200701-201512.nc

inputVarName = 'o3'
inputJson = '/Users/paul.smith/demo/Tables/SAGE-CCI-OMPS_input.json'
inputFilePathbgn = '/Users/paul.smith/demo/Data/OBS6_ESACCI-OZONE_sat_L3_AERmon_o3_198410-202212.nc'

###
f = xr.open_dataset(inputFilePathbgn,decode_times=False, decode_cf=False)
# f = f.bounds.add_missing_bounds(axes=['X', 'Y']) # ONLY IF BOUNDS NOT IN INPUT FILE
# f = f.bounds.add_bounds('T') # ONLY IF BOUNDS NOT IN INPUT FILE
d = f[inputVarName].values
vunits = f[inputVarName].units

### Initialize and run CMOR
cmor.setup(inpath='./',netcdf_file_action=cmor.CMOR_REPLACE_4 ,logfile='cmorLog.' + inputVarName + '.txt')
cmor.dataset_json(inputJson)
cmor.load_table(cmorTable)

cmorLat = cmor.axis("latitude", coord_vals=f.lat[:].values, cell_bounds=f.lat_bnds.values, units="degrees_north")
cmorLon = cmor.axis("longitude", coord_vals=f.lon[:].values, cell_bounds=f.lon_bnds.values, units="degrees_east")
cmorTime = cmor.axis("time", coord_vals=f.time.values, cell_bounds=f.time_bnds.values, units= f.time.units)
axes = [cmorTime, cmorLat, cmorLon]

############ DATASET SPECIFIC
if inputVarName in ['o3']:
    cmorLev = cmor.axis('alt41',coord_vals=f.alt16.values,units = 'km')
    axes = [cmorTime, cmorLev, cmorLat, cmorLon]
############

# Setup units and create variable to write using cmor - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_variable_attribute
varid   = cmor.variable(inputVarName,vunits,axes,missing_value=1.e20,positive="up")
values  = np.array(d[:],np.float32)

############ DATASET SPECIFIC # Adding o3 for the SAGE-CCI-OMPS+ dataset 
if inputVarName in ['o3']: varid = cmor.variable(inputVarName,vunits,axes,missing_value=1.e20,positive="up")
############

# Prepare variable for writing, then write and close file - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_variable_attribute
cmor.set_deflate(varid,1,1,1) ; # shuffle=1,deflate=1,deflate_level=1 - Deflate options compress file data
cmor.write(varid,values) ; # Write variable with time axis
f.close()
cmor.close()
print('done with ',inputVarName)
