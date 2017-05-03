#!/usr/bin/env python
"""
Title: calc_NetCDF_mean.py
Author: Nicholas Summons, n.summons@bom.gov.au
CreationDate: 2012-12-17

Description: 
            Function for calculating weighted average from multiple NetCDF files.
                        
            Input arguments:
                input_files:        List of input files.
                output_file:        Output file name.
                weighting_factors:  List of weightings for each file.
"""
import numpy
import netCDF4
import datetime


def calc_NetCDF_weighted_average(input_files, output_file, weighting_factors=None):
    
    nc = netCDF4.Dataset(input_files[0], mode='r')
    data_var_names = nc.variables.keys()
    nc.close()

    for k2, data_var_name in enumerate(data_var_names):

        for k, input_file in enumerate(input_files):

            # Open input file
            nc = netCDF4.Dataset(input_file, mode='r')

            data_var = nc.variables[data_var_name]
            data_var_attrs = data_var.ncattrs()

            if k == 0 and k2 == 0:

                # Create output file
                nc_out = netCDF4.Dataset(output_file, 'w', format='NETCDF4')

                # Create dimensions by replicating those in input file
                for dimName, dim in nc.dimensions.iteritems():
                    dimLen = len(dim)
                    if dim.isunlimited():
                        dimLen = 0
                    nc_out.createDimension(dimName, dimLen)

                # Copy global attributes
                attdict = nc.__dict__
                attdict['filename'] = unicode(output_file)

                # Append message to history attribute
                date_str = datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Y")
                log_str = ': Calculated weighted average.' + '\n  '
                if 'history' in attdict:
                    attdict['history'] = date_str + log_str + attdict['history']
                elif 'History' in attdict:
                    attdict['History'] = date_str + log_str + attdict['History']
                else:
                    attdict['history'] = date_str + log_str

                # Save global attributes
                for attr in attdict:
                    nc_out.setncattr(attr, attdict[attr])

            if k == 0:

                # Determine fill value
                if '_FillValue' in data_var_attrs:
                    fill_value = data_var.getncattr('_FillValue')
                elif 'missing_value' in data_var_attrs:
                    fill_value = data_var.getncattr('missing_value')
                else:
                    fill_value = None

                # Initialise masked array for calculating mean
                if fill_value is None:
                    sum_array = numpy.ma.zeros(data_var.shape)
                else:
                    sum_array = numpy.ma.zeros(data_var.shape, fill_value=fill_value)

                # Create data variable for storing calculated mean
                if fill_value is None:
                    data_var_mean = nc_out.createVariable(data_var_name, 'f', data_var.dimensions,
                                                          zlib=True, complevel=6)
                else:
                    data_var_mean = nc_out.createVariable(data_var_name, 'f', data_var.dimensions,
                                                          zlib=True, complevel=6, fill_value=fill_value)

                for attr in data_var_attrs:
                    if attr == '_FillValue':
                        continue
                    elif attr == 'scale_factor':
                        continue
                    elif attr == 'add_offset':
                        continue
                    data_var_mean.setncattr(attr, data_var.getncattr(attr))

            if weighting_factors is None:
                weighting_factor = 1.0
            else:
                weighting_factor = weighting_factors[k2]

            sum_array += data_var[:] * float(weighting_factor)

            # Close input file
            nc.close()

        data_var_mean[:] = sum_array / len(input_files)

    # Save data and close file
    nc_out.sync()
    nc_out.close()
