#
# (c) 2015 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

import os
import os.path
import glob
import calendar
from datetime import date

import numpy as np
import numpy.ma as ma

from ocean import util, config
from ocean.netcdf import SurfacePlotter
from ocean.datasets import SST
from ocean.netcdf import Grid, Gridset
from ocean.netcdf.extractor import Extractor, LandError
from ocean.config import regionConfig


#get the server dependant path configurations
serverCfg = config.get_server_config()

class ChlorophyllPlotterWrapper(SurfacePlotter):
    DATASET = 'chloro'
    PRODUCT_NAME = "Chlorophyll-A"

    FILL_VALUE = -32767.0

    VARIABLE_MAP = {
        'chldaily': 'chlor_a',
        'chlmonthly': 'chlor_a',
    }

    apply_to = util.Parameterise(SurfacePlotter)

    @apply_to(variable='chldaily')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'daily')

    @apply_to(variable='chlmonthly')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'monthly')

    # --- get_prefix ---
#    @apply_to(variable='chldaily')
    def get_prefix(self, params={}):
        return 'A'

#    @apply_to(variable='chlmonthly')
#    def get_prefix(self, params={}):
#        return 'A'

    @apply_to(variable='chldaily')
    def get_suffix(self, params={}):
        return '.L3m_DAY_CHL_chlor_a_4km' + self.FILE_EXTENSION

    @apply_to(variable='chlmonthly')
    def get_suffix(self, params={}):
        return '.L3m_MO_CHL_chlor_a_4km' + self.FILE_EXTENSION

    # --- get_title ---
    def get_title(self, params={}):
        title = 'Chlorophyll-A'
        return title

    def get_colormap(self, params={}):
        cm_name = 'jet'
        return cm_name

    @apply_to(variable='chldaily')
    def get_ticks(self, params={}):
        return np.array([0.01,0.03,0.05,0.07,0.1,0.15,0.2,0.3,0.5,1.0,2.0,3.0,5.0,10.0]) 

    @apply_to(variable='chlmonthly')
    def get_ticks(self, params={}):
        return np.array([0.01,0.03,0.05,0.07,0.1,0.15,0.2,0.3,0.5,1.0,2.0,3.0,5.0,10.0]) 

    def get_ticks_format(self, params={}):
        return '%.2f'

    def get_colormap_strategy(self, params={}):
        return 'nonlinear'

#    def get_colormap(self, params={}):
#        return 'coolwarm'

#    @apply_to(variable='daily', period='daily')
#    def get_formatted_date(self, params={}):
#        date = params['date'].timetuple()
#        return '%4d%03d' % (date.tm_year, date.tm_yday)

    def get_plotstyle(self, params={}):
        return 'pcolormesh'
  
    def get_extend(self, params={}):
        return 'neither'

    def get_fill_color(self, params={}):
       # return '1.0'
        return '0.98'

    @apply_to(variable='chldaily')
    def get_units(self, params={}):
        return 'mg/m' + ur'\u00B3'

    @apply_to(variable='chlmonthly')
    def get_units(self, params={}):
        return 'mg/m' + ur'\u00B3' 

    @apply_to(variable='chldaily')
    def get_contourlines(self, params={}):
        return False

    @apply_to(variable='chlmonthly')
    def get_contourlines(self, params={}):
        return False

    @apply_to(variable='chldaily', period='daily')
    def get_grid(self, params={}, **kwargs):
        """
        Request a Grid object for this dataset.

        Override this method to access grids in a different way.
        """

        gridvar = self.get_variable_mapping(params=params)
        grid =  ChlorophyllGridset(self.get_path(params=params), gridvar, params['period'],
                       prefix=self.get_prefix(params=params),
                       suffix=self.get_suffix(params=params),
                       suffix2=self.get_suffix_prelim(params=params),
                       date=params['date'],
                       **kwargs)
        return grid

    @apply_to(variable='chlmonthly', period='monthly')
    def get_grid(self, params={}, **kwargs):
        """
        Request a Grid object for this dataset.

        Override this method to access grids in a different way.
        """

        gridvar = self.get_variable_mapping(params=params)
        grid =  ChlorophyllMonthlyGridset(self.get_path(params=params), gridvar, params['period'],
                       prefix=self.get_prefix(params=params),
                       suffix=self.get_suffix(params=params),
                       suffix2=self.get_suffix_prelim(params=params),
                       date=params['date'],
                       **kwargs)
        return grid
  
    def extract(self, **args):

        area = args['area']
        variable = args['variable']
        inputLat = args['lat']
        inputLon = args['lon']

#        lat_min = regionConfig.regions[area][1]['llcrnrlat']
#        lat_max = regionConfig.regions[area][1]['urcrnrlat']
#        lon_min = regionConfig.regions[area][1]['llcrnrlon']
#        lon_max = regionConfig.regions[area][1]['urcrnrlon']

#        grid = self.get_grid(params=args,
#                             lonrange=(lon_min, lon_max),
#                             latrange=(lat_min, lat_max))

        grid = self.get_grid(params=args)

        #extract lat/lon and value
        (lat, lon), (latIndex, lonIndex) = Extractor.getGridPoint(inputLat, inputLon, grid.lats, grid.lons,
                                                     grid.data)
        value = grid.data[latIndex, lonIndex]
        if value is ma.masked or value == self.FILL_VALUE:
            raise LandError()
        #return extracted value
        return (lat, lon), value


class ChlorophyllGridset(Gridset):
 
    # a list of possible variables for latitudes
    LATS_VARIABLE = ['lat']

    # a list of possible variables for longitude
    LONS_VARIABLE = ['lon']

    def get_filename_date(self, date, **kwargs):
        date = date.timetuple()
        return '%4d%03d' % (date.tm_year, date.tm_yday)

class ChlorophyllMonthlyGridset(ChlorophyllGridset):
 
    def get_filename_date(self, date, **kwargs):
        first_day_month = date.replace(day=1)
        last_day_month = date.replace(day=calendar.monthrange(date.year, date.month)[1])

        first_date = first_day_month.timetuple()
        last_date = last_day_month.timetuple()
        return '%4d%03d%4d%03d' % (first_date.tm_year, first_date.tm_yday, last_date.tm_year, last_date.tm_yday)

class chlorophyll(SST):
    DATASET = 'chloro'
    PLOTTER = ChlorophyllPlotterWrapper

    __periods__ = [
        'daily',
        'monthly',
    ]

    __subdirs__ = [
        'daily',
        'monthly',
    ]

    __plots__ = [
        'map',
        'point'
    ]

    __variables__ = [
        'chldaily',
        'chlmonthly'
    ]

    def preprocess(self, fileName, **params):
        '''
            Allows the map images to be produced via the URL.
        '''
        self.plotter.plot(fileName, **params)
