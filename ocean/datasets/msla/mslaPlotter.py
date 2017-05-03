#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

import os
import os.path
import glob
import numpy as np
import numpy.ma as ma
from datetime import datetime, timedelta

from ocean import config, logger, util
from ocean.config import regionConfig
from ocean.netcdf.surfaceplotter import SurfacePlotter
from ocean.netcdf import Gridset
from ocean.netcdf.extractor import Extractor, LandError

serverCfg = config.get_server_config()
    
DATASET = 'msla'

class MslaPlotter(SurfacePlotter):
    DATASET = DATASET
    
    VARIABLE_MAP = {
        'sla': 'sla'
    }
    
    apply_to = util.Parameterise()
    
    PRODUCT_NAME = "AVISO Ssalto/Duacs SLA"
    
    def __init__(self, variable):
        super(MslaPlotter, self).__init__()
            
    def get_colormap_strategy(self, params={}):
        return 'nonlinear'
    
    def get_grid(self, params, **kwargs):
        gridvar = params['variable'] 
        grid =  MslaGrid(self.get_path(params=params), gridvar, params['period'],
                       prefix=self.get_prefix(params=params),
                       suffix=self.get_suffix(params=params),
                       suffix2=self.get_suffix_prelim(params=params),
                       date=params['date'],
                       **kwargs)
        return grid
    
    def get_ticks(self, params={}):
        return np.arange(-0.3,0.31,0.05)

    def get_ticks_format(self, params={}, **kwargs):
        return '%.0f'
    
    def get_units(self, params={}, **kwargs):
        return 'mm'
    
    @apply_to(variable='sla')
    def get_labels(self, params={}):
        return (((self.get_ticks(params=params) * 1000).astype(np.float16)).astype(int), None)
    
    @apply_to(variable='sla')
    def get_smooth_fac(self, params={}):
        try:
            if regionConfig.regions[params['area']][0] == 'pac':
                return 1
            else:
                pass
        except KeyError:
            pass
        return 30

    @apply_to(period='daily')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET], 'grids', 'daily')

    @apply_to(period='monthly')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET], 'grids', 'monthly')

    @apply_to(period='daily')
    def get_prefix(self, params={}):
        return 'nrt_global_allsat_msla_h_'

    @apply_to(period='monthly')
    def get_prefix(self, params={}):
        return 'nrt_sea_level_'
    
    def extract(self, **args):

        area = args['area']
        variable = args['variable']
        inputLat = args['lat']
        inputLon = args['lon']

#        lat_min = regionConfig.regions[area][1]['llcrnrlat']
#        lat_max = regionConfig.regions[area][1]['urcrnrlat']
#        lon_min = regionConfig.regions[area][1]['llcrnrlon']
#        lon_max = regionConfig.regions[area][1]['urcrnrlon']
#
#        grid = self.get_grid(params=args,
#                             lonrange=(lon_min, lon_max),
#                             latrange=(lat_min, lat_max))

        grid = self.get_grid(params=args)

        #extract lat/lon and value
        (lat, lon), (latIndex, lonIndex) = Extractor.getGridPoint(inputLat, inputLon, grid.lats, grid.lons,
                                                     grid.data)
        value = grid.data[latIndex, lonIndex]
        value = value * 1000
        if value is ma.masked:
            raise LandError()
        #return extracted values
        return (lat, lon), value

class MslaGrid(Gridset):

    def get_filename(self, path, prefix, suffix, date, period):
        """
        Get the file based on the given date
        """
        return getFileForTheDate(path, prefix, date, period)

"""
Get the file based on the given date
"""
def getFileForTheDate(path, prefix, date, period):

    if period == 'daily':
        formatted_date = date.strftime('%Y%m%d')
        file_name = prefix + formatted_date + '_'+ formatted_date + '.nc'
    elif period == 'monthly':
        formatted_date = date.strftime('%Y%m')
        file_name = prefix + formatted_date + '.nc'

    file_name_with_path = os.path.join(path, file_name)
    return file_name_with_path
