#!/uasr/bin/env python
#
# (c) 2013 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Grant Smith <grsmith@bom.gov.au>
# Date: 14/1/2014
# Purpose: Extract MUR SST data and front detection (and calculate gradients)
# subroutines: extract_sst, calc_grad, front_detection, create_nc

from netCDF4 import Dataset
import numpy as np
import math
import datetime
import shapefile
import sys
import os
#sys.path.insert(0,'/home/gsmith/map-portal5/map-portal')
from ocean.config.regionConfig import regions

def Download_MUR(data_dir,data_subdir,server,server_path, day, month, year, reg_name):
    mur_path=data_dir+'/'+data_subdir
    gridcell = 360/float(32768)
    variable_name='analysed_sst'
    temp_offset=-273.15
    #print out ASCII grids
    ascii_flag=False
    time_unit='seconds since 1981-01-01 00:00:00 UTC'

    latStart=regions[reg_name][1]['llcrnrlat']
    latEnd=regions[reg_name][1]['urcrnrlat']
    lonStart=regions[reg_name][1]['llcrnrlon']
    lonEnd=regions[reg_name][1]['urcrnrlon']

    day_of_year=(datetime.datetime(year=year, month=month, day=day)-datetime.datetime(year,1,1)).days +1
    filename=str(year)+str(month).zfill(2)+str(day).zfill(2)+'-JPL-L4UHfnd-GLOB-v01-fv04-MUR.nc.bz2'
    total_name=server+server_path+'/'+str(year)+'/'+str(day_of_year).zfill(3)+'/'+filename
    #total_name='/home/gsmith/MUR/20150715-JPL-L4UHfnd-GLOB-v01-fv04-MUR.nc.bz2'

    if not os.path.exists(mur_path+'/'+reg_name):
        os.makedirs(mur_path+'/'+reg_name)
    output_filename=mur_path+'/'+reg_name+'/MUR_'+str(year)+str(month).zfill(2)+str(day).zfill(2)+'_'+reg_name
    if (lonEnd<180):
      lonCellStart=int((lonStart+180)/gridcell)
      lonCellEnd=int((lonEnd+180)/gridcell)
      lonRange=range(lonCellStart,lonCellEnd)
    elif (lonStart>180):
      lonCellStart=int((lonStart-180)/gridcell)
      lonCellEnd=int((lonEnd-180)/gridcell)
      lonRange=range(lonCellStart,lonCellEnd)
    else:
      lonCellStart1=int((lonStart+180)/gridcell)
      lonCellEnd1=32768
      lonCellStart2=0
      lonCellEnd2=int((lonEnd-180)/gridcell)
      lonRange=range(lonCellStart1,lonCellEnd1)+range(lonCellStart2,lonCellEnd2)

    latCellStart=int((90+latStart)/gridcell)
    latCellEnd=int((90+latEnd)/gridcell)
    latRange=range(latCellStart,latCellEnd)
    lat,lon,sst_data,sst_time=extract_sst(total_name,lonRange,latRange,variable_name,temp_offset)
    gradient_data=calc_grad(sst_data,lon,lat)
    front_data=front_detect(sst_data,lon,lat,gradient_data,output_filename)
    create_nc(output_filename,len(lonRange),len(latRange),'sst',lat,lon,sst_data,gradient_data,front_data,sst_time,time_unit,gridcell,temp_offset,ascii_flag)

def extract_sst(filename,lonRange,latRange,nc_data_name,temp_offset):

    cdf1=Dataset(filename,'r')
    data_var_names=cdf1.variables.keys()
    lat=np.empty([len(latRange)])
    lon=np.empty([len(lonRange)])
    sst=np.empty([len(latRange),len(lonRange)])

    lat[:]=cdf1.variables["lat"][latRange]
    lon[:]=cdf1.variables["lon"][lonRange]
    sst[:,:]=cdf1.variables[nc_data_name][0,latRange,lonRange]
    time=cdf1.variables["time"][0]
    #sst=sst-temp_offset
    cdf1.close()
    return lat,lon,sst,time

def calc_grad(sst_array,lon,lat):
	grad=np.empty([len(lat),len(lon)])
	for y in range(0,len(lat)):
            for x in range(0,len(lon)):
		if x==0 or y==0 or x==len(lon)-1 or y==len(lat)-1:
			grad[y,x]=0
		else:
                        grad_x=(sst_array[y,x+1]-sst_array[y,x-1])/((2*(lon[x]-lon[x-1]))*60*1.852*math.cos(math.radians(lat[y])))
                        grad_y=(sst_array[y+1,x]-sst_array[y-1,x])/((2*(lat[y]-lat[y-1]))*60*1.852)
			grad[y,x]=(grad_x**2+grad_y**2)**0.5

	return grad

def front_detect(sst_array,lon,lat,grad,out_file):

	outpic=np.zeros([len(lat),len(lon)])
	
	WinSize=100
	nsd2=WinSize/2
	HistoRange=255
	threshold=0.73
	grad_thresh=0.01
	minstep=3
	delta_temp=0.5
	num_win_x=int(len(lon)/nsd2)
	num_win_y=int(len(lat)/nsd2)
	w=shapefile.Writer(shapefile.POINT)
	w.field('Delta_Temp','F',10,5)
	w.field('Max_Grad','F',10,5)
	w.field('Threshold','F',10,5)
	shp_flag=False
	for x in range(0,num_win_x-1):
		for y in range(0,num_win_y-1):
		  count=np.zeros([HistoRange])
		  pict=np.empty([WinSize,WinSize])
		  pict_grad=np.empty([WinSize,WinSize])
		  pict2=np.empty([WinSize,WinSize])
		  pict2.fill(255)
		  pict[:,:]=sst_array[y*nsd2:(y*nsd2)+WinSize,x*nsd2:(x*nsd2)+WinSize]
		  pict_masked=np.ma.masked_less(pict,0)
		  pict_grad[:,:]=grad[y*nsd2:(y*nsd2)+WinSize,x*nsd2:(x*nsd2)+WinSize]
		  max_pict=pict_masked.max()
		  min_pict=pict_masked.min()
		  if max_pict-min_pict>delta_temp and pict_grad.max()>grad_thresh:
			diff_pict=(max_pict-min_pict)/HistoRange
			histo_map=np.arange(min_pict,max_pict,diff_pict)
			for i in range(0,WinSize):
				for j in range(0,WinSize):
					if pict[i,j]>0:
						if int((pict[i,j]-min_pict)/diff_pict)==255:
							pict2[i,j]=254
						else:
							pict2[i,j]=int((pict[i,j]-min_pict)/diff_pict)
			for i in range(0,WinSize):
				for j in range(0,WinSize):
					if (pict2[i,j]>2 and pict2[i,j]<255):
						count[pict2[i,j]]=count[pict2[i,j]]+1
			sum=0
			total=0
			ssq=0
			na=np.empty([HistoRange])
			suma=np.empty([HistoRange])
			ssqa=np.empty([HistoRange])
			nb=np.empty([HistoRange])
			sumb=np.empty([HistoRange])
			ssqb=np.empty([HistoRange])
			tcond=np.empty([HistoRange])
			meana=np.empty([HistoRange])
			meanb=np.empty([HistoRange])
			dif=np.empty([HistoRange])
			for i in range(0,HistoRange):
				if count[i]!=0:
					total=count[i]+total
					sum=count[i]*i+sum
					ssq=ssq+(count[i]*i*i)
				na[i]=total
				suma[i]=sum
				ssqa[i]=ssq

			for i in range(0,HistoRange):
				nb[i]=total-na[i]
				sumb[i]=sum-suma[i]
				ssqb[i]=ssq-ssqa[i]
				tcond[i]=(na[i]!=0 and nb[i]!=0)
				if tcond[i]:
					meana[i]=suma[i]/na[i]
					meanb[i]=sumb[i]/nb[i]

			max=np.zeros(3)
			index=HistoRange+1
			for i in range(0,HistoRange):
				if tcond[i]:
					dif[i]=na[i]*nb[i]*((meana[i]-meanb[i])**2)
					if max[0]<dif[i]:
						max[0]=dif[i]
						index=i

			if total>100 and index!=HistoRange+1:
				s_pop=min(na[index],nb[index])
				if s_pop*4>total:
					sum=sum/total
					var=ssq-((sum**2)*total)
					if var!=0:
						max[0]=max[0]/(var*total)
						max[1]=meana[index]
						max[2]=meanb[index]	
				else:
					max[0]=0
			else:
				max[0]=0
			shp_file=[]
			shp_points=False
			if max[0]>threshold and (max[2]-max[1])>minstep:
	                        for i in range(0,WinSize-1):
        	                        for j in range(0,WinSize-1):
						if pict2[i,j]>index and pict2[i,j]<255:
							if (pict2[i+1,j]<=index or pict2[i,j+1]<=index) and pict2[i+1,j]<255 and  pict2[i,j+1]<255:# and grad[y*nsd2+i,x*nsd2+j]>grad_thresh:
								outpic[y*nsd2+i,x*nsd2+j]=1
								shp_file.append([lat[y*nsd2+i],lon[x*nsd2+j]])
								shp_points=True
								shp_flag=True
						else:
                                                        if (pict2[i+1,j]>=index or pict2[i,j+1]>=index) and pict2[i+1,j]<255 and pict2[i,j+1]<255:# and grad[y*nsd2+i,x*nsd2+j]>grad_thresh:
                                                                outpic[y*nsd2+i,x*nsd2+j]=1
								shp_file.append([lat[y*nsd2+i],lon[x*nsd2+j]])
								shp_points=True
								shp_flag=True

			if shp_points:
                                        #w=shapefile.Writer(shapefile.POLYLINE)
                                        #w.line(parts=[shp_file])
				for k in range(len(shp_file)): 
	                        	w.point(shp_file[k][1],shp_file[k][0])
                                        w.record(max_pict-min_pict,pict_grad.max(),max[0])
	if shp_flag:
		w.save(out_file+'.shp')
	return outpic
	
def create_nc(output_filename,lon_len,lat_len,var_name,lat_array,lon_array,sst,gradient,front_data,data_time,time_unit,gridcell,temp_offset,ascii_flag):
	for i in range(len(lon_array)):
		if lon_array[i]<0:
			lon_array[i]=lon_array[i]+360
        nc_pointer = Dataset(output_filename+'.nc', 'w', format='NETCDF4')
	nc_pointer.set_fill_on()

	time_dim=nc_pointer.createDimension('time',1)
	nc_time=nc_pointer.createVariable('time','f4',('time',))
	nc_time.setncattr('long_name','Center time of the day')
	nc_time.setncattr('units',time_unit)
	nc_time[0]=data_time

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
	data = nc_pointer.createVariable(var_name,'f4',(u'time',u'lat',u'lon'),zlib=True,complevel=6,fill_value=-999)
	#data2 = nc_pointer.createVariable('gradient','f4',(u'time',u'lat',u'lon'),zlib=True,complevel=6,fill_value=-999)
	#data3=nc_pointer.createVariable('fronts','i',(u'time',u'lat',u'lon'),zlib=True,complevel=6,fill_value=-999)
        data[0,:,:]=sst
	#data3[0,:,:]=front_data

	data.setncattr('long_name','Sea Surface Temperature')
	data.setncattr('units','degrees C')
	data.setncattr('add_offset',temp_offset)
	data.setncattr('scale_factor',1)
	data.setncattr('valid_min',-3)
	data.setncattr('valid_max',45)

        #data2.setncattr('long_name','Gradients')
        #data2.setncattr('units','degrees/km')
        #data2.setncattr('add_offset',0)
        #data2.setncattr('scale_factor',1)
        #data2.setncattr('valid_min',0)
        #data2.setncattr('valid_max',1)

        #data3.setncattr('long_name','Fronts')
        #data3.setncattr('units','binary')
        #data3.setncattr('add_offset',0)
        #data3.setncattr('scale_factor',1)
        #data3.setncattr('valid_min',0)
        #data3.setncattr('valid_max',1)

	#data[0,0,:,:]=data_array
	if ascii_flag:
		ascii_grid=open(output_filename+'_sst.asc',"w")
		ascii_grid.write("ncols "+str(lon_len)+ '\n')
        	ascii_grid.write("nrows "+str(lat_len)+ '\n')
		ascii_grid.write("xllcorner "+str(lon_array.min())+ '\n')
		ascii_grid.write("yllcorner "+str(lat_array.min())+ '\n')
		ascii_grid.write("cellsize "+str(gridcell)+ '\n')
		ascii_grid.write("NODATA_value -32.768"+ '\n')
		np.savetxt(ascii_grid,np.flipud(sst),fmt='%.10e')
		ascii_grid.close()

		ascii_grid=open(output_filename+'_grad.asc',"w")
        	ascii_grid.write("ncols "+str(lon_len)+ '\n')
        	ascii_grid.write("nrows "+str(lat_len)+ '\n')
        	ascii_grid.write("xllcorner "+str(lon_array.min())+ '\n')
        	ascii_grid.write("yllcorner "+str(lat_array.min())+ '\n')
        	ascii_grid.write("cellsize "+str(gridcell)+ '\n')
        	ascii_grid.write("NODATA_value -32.768"+ '\n')
        	np.savetxt(ascii_grid,np.flipud(gradient),fmt='%.10e')
        	ascii_grid.close()

        	ascii_grid=open(output_filename+'_front.asc',"w")
        	ascii_grid.write("ncols "+str(lon_len)+ '\n')
        	ascii_grid.write("nrows "+str(lat_len)+ '\n')
        	ascii_grid.write("xllcorner "+str(lon_array.min())+ '\n')
        	ascii_grid.write("yllcorner "+str(lat_array.min())+ '\n')
        	ascii_grid.write("cellsize "+str(gridcell)+ '\n')
        	ascii_grid.write("NODATA_value -32.768"+ '\n')
        	np.savetxt(ascii_grid,np.flipud(front_data),fmt='%.10e')
        	ascii_grid.close()
	
	nc_pointer.sync()
	nc_pointer.close()

if __name__ == "__main__":

	main()
