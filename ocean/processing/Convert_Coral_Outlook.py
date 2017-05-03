#!/usr/bin/env python
#
# (c) 2013 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Grant Smith <grsmith@bom.gov.au>
# Date: 14/1/2015
# Purpose: Convert Coral Bleaching Outlook Binaries from Coral Reef Watch

from netCDF4 import Dataset,date2num
import numpy as np
#np.set_printoptions(threshold=np.inf)
import math
import datetime
import os
import re

def Convert_Outlook(data_dir,data_subdir):

	path=data_dir+'/'+data_subdir
        lat_array=np.arange(-89.75,90,0.5)
        lon_array=np.arange(0.25,360,0.5)

	lat_len=len(lat_array)
	lon_len=len(lon_array)

	var_name='BAA'
	gridcell=0.5
        time_unit = 'hours since 1900-01-01 00:00:00.0'
        time_calendar = 'gregorian'
	num_weeks=37
	num_ens=28
	#create file list from files that have been downloaded
	files= [f for f in os.listdir(path) if f.endswith(".dat")]

	for num_file in range(0,len(files)):
		filename=files[num_file]
		date_stamp=re.findall('\d+',filename)
		year=int(date_stamp[3])/10000
		month=(int(date_stamp[3])-(year*10000))/100
		day=(int(date_stamp[3])-(year*10000)-(month*100))
		out_filename=path+'/'+files[num_file][0:44]+'.nc'

		print out_filename

		if not os.path.isfile(out_filename):#process if netcdf file doesn't exist yet
			f=open(path+'/'+filename,'rb')
			nc_pointer=Dataset(out_filename,'w','NETCDF4')
		        nc_pointer.set_fill_on()
			dates=[]
			for n in range(0,num_weeks):
				if n in (1,5,9):#only store the three outlook start dates
					dates.append(datetime.datetime(year,month,day)+n*datetime.timedelta(days=7))
			time_dim=nc_pointer.createDimension('time',3)#only store the outlooks
		        #time_dim=nc_pointer.createDimension('time',37)
		        nc_time=nc_pointer.createVariable('time','f4',('time',))
		        nc_time.setncattr('long_name','Center time of the day')
	        	nc_time.setncattr('units',time_unit)
			nc_time[:]=date2num(dates,units=time_unit,calendar=time_calendar)
			#no need to store essemble in final
			#ens_dim=nc_pointer.createDimension('ensemble',28)
		        #nc_ens=nc_pointer.createVariable('ensemble','f4',('ensemble',))
		        #nc_ens.setncattr('long_name','Ensemble Number')
	        	#nc_ens.setncattr('units','ensemble number')
		        #nc_ens[:]=range(1,29)
		
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
#       	        data = nc_pointer.createVariable(var_name,'f4',(u'time',u'ensemble',u'lat',u'lon'),zlib=True,complevel=6,fill_value=-999)
        		#data = nc_pointer.createVariable(var_name,'f4',(u'time',u'lat',u'lon'),zlib=True,complevel=6,fill_value=-999)
        		data = nc_pointer.createVariable(var_name,'f4',(u'time',u'lat',u'lon'),zlib=True,complevel=6,fill_value=255)
			z=0#the date storage number, is 0,1,2
			baa=np.zeros(shape=(360,720))
			for x in range(0,num_weeks):
				for y in range(0,num_ens):
					baa_raw=np.fromfile(f,np.dtype(np.uint8),count=259200)
					if y==11: #the ensemble we are after, 3 is 90%, 11 is 60%
						baa=np.maximum(baa,np.reshape(baa_raw,(360,720)))
						#baa=np.reshape(baa_raw,(138,360))
						if x in (4,8,12):
						        data[z,:,:]=baa
							z=z+1
							baa=np.zeros(shape=(360,720))
	
	
			data.setncattr('long_name','Bleaching Alert Areas')
			data.setncattr('units','Alert Level')
			data.setncattr('add_offset',0)
			data.setncattr('scale_factor',1)
			data.setncattr('valid_min',0)
			data.setncattr('valid_max',4)
	
			nc_pointer.sync()
			nc_pointer.close()
			f.close()
