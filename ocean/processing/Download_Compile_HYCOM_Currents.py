#!/usr/bin/env python
#
# (c) 2013 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Grant Smith <grsmith@bom.gov.au>
# Date: 17/3/2015
# Purpose: Download Forecast HYCOM currents and compile into one NETCDF File

from netCDF4 import Dataset
import numpy as np
import math
import datetime
import os.path
#np.set_printoptions(threshold=np.nan)
#from ocean.config import get_server_config

def Download_Compile_HYCOM_Currents(data_dir,data_subdir,server,server_path):

    #Set output path for final NETCDF file    
    #config=get_server_config() 
    path=data_dir+'/'+data_subdir

#--------User Input Variables------------#
    latStart = -80
    latEnd = 80
    lonStart = 110
    lonEnd = 290
#    num_of_time_steps=57
#    num_of_time_steps=24
    start_timestamp=8
    end_timestamp=32
    num_of_time_steps=end_timestamp - start_timestamp

    output_filename=path+'/'+'latest_HYCOM_currents.nc'           

        #URL='http://tds.hycom.org/thredds/dodsC/GLBu0.08/expt_91.1/forecasts'
    gridcell = 0.08
    variable_name1='water_u'        
    variable_name2='water_v'
    temp_offset=0
    time_unit='hours since 2000-01-01 00:00:00'
#----------------------------------------#
    #Determine array cell references
    lonCellStart=int((lonStart)/gridcell)
    lonCellEnd=int((lonEnd)/gridcell)
    lonRange=range(lonCellStart,lonCellEnd+1)
    latCellStart=int((80+latStart)/gridcell)
    latCellEnd=int((80+latEnd)/gridcell)
    latRange=range(latCellStart,latCellEnd+1)

    try: #Test to see whether yesterdays data is in, if not, pick the day before
        d=datetime.date.today()-datetime.timedelta(days=1)
        filename='hycom_glb_912_'+str(int(d.year))+str(int(d.month)).zfill(2)+str(int(d.day)).zfill(2)+'00_t'+str(start_timestamp*3).zfill(3)+'_uv3z.nc'
        total_name=server+server_path+'/'+filename
        cdf1=Dataset(total_name,'r')
    except:
        d=datetime.date.today()-datetime.timedelta(days=2)
        filename='hycom_glb_912_'+str(int(d.year))+str(int(d.month)).zfill(2)+str(int(d.day)).zfill(2)+'00_t'+str(start_timestamp*3).zfill(3)+'_uv3z.nc'
        total_name=server+server_path+'/'+filename
        cdf1=Dataset(total_name,'r')

    for x in range(start_timestamp,end_timestamp,2):
        if x==start_timestamp:
            #If first iteration, extract all data including lat and lon and create output netcdf
            lat,lon,water_u,water_v,time=extract_all(cdf1,lonRange,latRange,variable_name1,variable_name2)
            create_nc(output_filename,len(lonRange),len(latRange),'u','v',lat,lon,time_unit,gridcell,num_of_time_steps/2)
            #Append data to netcdf
            add_nc(output_filename,'u','v',water_u,water_v,time,0)
        else:
            filename='hycom_glb_912_'+str(int(d.year))+str(int(d.month)).zfill(2)+str(int(d.day)).zfill(2)+'00_t'+str(x*3).zfill(3)+'_uv3z.nc'
            total_name=server+server_path+'/'+filename
            cdf1=Dataset(total_name,'r')
            #Only extract data and time stamp on subsequent iterations
            water_u,water_v,time=extract_data(cdf1,lonRange,latRange,variable_name1,variable_name2)
            index = (x-start_timestamp)/2
            add_nc(output_filename,'u','v',water_u,water_v,time,index)

        

def extract_all(cdf1,lonRange,latRange,nc_data_name1,nc_data_name2):
    
    data_var_names=cdf1.variables.keys()
    lat=np.squeeze(cdf1.variables["lat"][latRange])
    lon=np.squeeze(cdf1.variables["lon"][lonRange])
    data=cdf1.variables[nc_data_name1]
    data=cdf1.variables[nc_data_name1][0,0,latRange,lonRange]
    data2=cdf1.variables[nc_data_name2][0,0,latRange,lonRange]
    time=cdf1.variables["time"][0]
    cdf1.close()
    return lat,lon,data,data2,time

def extract_data(cdf1,lonRange,latRange,nc_data_name1,nc_data_name2):

    data_var_names=cdf1.variables.keys()
    data=cdf1.variables[nc_data_name1][0,0,latRange,lonRange]
    data2=cdf1.variables[nc_data_name2][0,0,latRange,lonRange]
    time=cdf1.variables["time"][0]
    cdf1.close()
    return data,data2,time


def create_nc(output_filename,lon_len,lat_len,var_name1,var_name2,lat_array,lon_array,time_unit,gridcell,num_time_steps):
    nc_pointer = Dataset(output_filename, 'w', format='NETCDF4')
    nc_pointer.set_fill_on()

    time_dim=nc_pointer.createDimension('time',num_time_steps)
    nc_time=nc_pointer.createVariable('time','f4',('time',))
    nc_time.setncattr('long_name','Valid Time')
    nc_time.setncattr('units',time_unit)
    nc_time.setncattr('calendar','gregorian')

    lat_dim=nc_pointer.createDimension('lat',lat_len)
    lat=nc_pointer.createVariable('lat','f4',('lat',))
    lat.setncattr('long_name','Latitude')
    lat.setncattr('units','degrees_north')
    lat.setncattr('grids', 'Uniform grid from '+str(lat_array[0])+' to '+str(lat_array[lat_len-1])+' by '+str(gridcell))
    lat[:]=lat_array

    lon_dim=nc_pointer.createDimension('lon',lon_len)
    lon=nc_pointer.createVariable('lon','f4',('lon',))
    lon.setncattr('long_name','Longitude')
    lon.setncattr('units','degrees_east')
    lon.setncattr('grids','Uniform grid from '+str(lon_array[0])+' to '+str(lon_array[lon_len-1])+' by '+str(gridcell))
    lon[:]=lon_array

    data = nc_pointer.createVariable(var_name1,'f4',(u'time',u'lat',u'lon'),zlib=True,complevel=6,fill_value=-30000)
    data2= nc_pointer.createVariable(var_name2,'f4',(u'time',u'lat',u'lon'),zlib=True,complevel=6,fill_value=-30000)

    data.setncattr('long_name','Eastward Water Velocity')
    data.setncattr('standard_name','eastward_sea_water_velocity')
    data.setncattr('units','m/s')
    data.setncattr('add_offset',0)
    data.setncattr('scale_factor',0.001)
    data.setncattr('valid_min',-50)
    data.setncattr('valid_max',50)

    data2.setncattr('long_name','Northward Water Velocity')
    data2.setncattr('standard_name','northward_sea_water_velocity')
    data2.setncattr('units','m/s')
    data2.setncattr('add_offset',0)
    data2.setncattr('scale_factor',0.001)
    data2.setncattr('valid_min',-50)
    data2.setncattr('valid_max',50)

    nc_pointer.sync()
    nc_pointer.close()


def add_nc(output_filename,var_name1,var_name2,raw_data1,raw_data2,data_time,x):
    nc_pointer = Dataset(output_filename, 'r+', format='NETCDF4')
    nc_pointer.set_fill_on()

    nc_time=nc_pointer.variables['time']
    nc_time[x]=data_time
    data=nc_pointer.variables[var_name1]
    data[x,:,:]=raw_data1
    data2=nc_pointer.variables[var_name2]
    data2[x,:,:]=raw_data2

    nc_pointer.sync()
    nc_pointer.close()
