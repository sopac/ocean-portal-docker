#
# (c) 2015 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

import os
import os.path
import glob
from datetime import datetime, timedelta

import numpy as np
import numpy.ma as ma

from ocean import util, config
from ocean.config import productName
from ocean.netcdf import SurfacePlotter
from ocean.plotter import Plotter
from ocean.datasets import SST
from ocean.netcdf import Gridset
from ocean.netcdf.extractor import Extractor, LandError
from ocean.config import regionConfig

from coralAlert import filter_alert

#get the server dependant path configurations
serverCfg = config.get_server_config()

class CoralPlotterWrapper(SurfacePlotter):
    DATASET = 'coral'
    PRODUCT_NAME = "NOAA Coral Reef Watch"

    VARIABLE_MAP = {
        'daily': 'CRW_BAA_max7d',
        'outlook': 'BAA',
    }

    apply_to = util.Parameterise(SurfacePlotter)

    @apply_to(variable='daily')
    def get_path(self, params={}):
        year = params['date'].year
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'daily', str(year))

    @apply_to(variable='outlook')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'outlook')

    # --- get_prefix ---
#    @apply_to(variable='daily')
#    def get_prefix(self, params={}):
#        return 'baa_max_r07d_b05kmnn_'
#
#    @apply_to(variable='outlook')
#    def get_prefix(self, params={}):
#        return 'outlook_srt_v3_wk_among28_cfsv2_icwk'
#
    def get_prefix(self, params={}):
        prefix = ''
        if params['variable'] == 'daily':
            prefix = 'baa_max_r07d_b05kmnn_'
        else:
            prefix = 'outlook_srt_v3_wk_among28_cfsv2_icwk'
        return prefix 

    def get_formatted_date(self, params={}):
        formatted_date = ''
        path = getLastestFile(self.get_path(params = params))
        refDate = datetime.strptime(path[-11:-3], '%Y%m%d')         
        startDate = refDate + timedelta(7)
        
        if params['period'] == 'daily':
                formatted_date = params['date'].strftime('%d %B %Y')
        if params['period'] == '4weeks':
            formatted_date = startDate.strftime('%d %B %Y')
        elif params['period'] == '8weeks':
            incDate = startDate + timedelta(weeks=4)
            formatted_date = incDate.strftime('%d %B %Y')
        elif params['period'] == '12weeks':
            incDate = startDate + timedelta(weeks=8)
            formatted_date = incDate.strftime('%d %B %Y')
        return formatted_date

    # --- get_title ---
#    @apply_to(variable='daily')
    def get_title(self, params={}):
        title = ''
        if (params['variable'] == 'daily'):
            title = 'Coral Bleaching Alert'
        else: 
            title = 'Coral Bleaching Outlook'
        return title

    @apply_to(variable='daily')
    def get_ticks(self, params={}):
        return np.arange(6) 

    @apply_to(variable='outlook')
    def get_ticks(self, params={}):
        return np.arange(6) 

    @apply_to(variable='daily')
    def get_colors(self, params={}):
        return np.array([[200, 250, 250],
                         [255, 240, 0],
                         [250, 170, 10],
                         [240, 0, 0],
                         [150, 0, 0]])
   
    @apply_to(variable='daily')
    def get_basemap_colors(self, params={}):
        return np.array([[255, 255, 255],
                         [191, 191, 191],
                         [128, 128, 128],
                         [64, 64, 64],
                         [0, 0, 0]])

    @apply_to(variable='outlook')
    def get_colors(self, params={}):
        return np.array([[200, 250, 250],
                         [255, 210, 160],
                         [250, 170, 10],
                         [240, 0, 0],
                         [150, 0, 0]])

    @apply_to(variable='outlook')
    def get_basemap_colors(self, params={}):
        return np.array([[255, 255, 255],
                         [191, 191, 191],
                         [128, 128, 128],
                         [64, 64, 64],
                         [0, 0, 0]])

    def get_fill_color(self, params={}):
        #return '0.59'
        return '0.98'

    def get_colormap_strategy(self, params={}):
        return 'levels'

    #@apply_to(variable='daily')
    def get_plotstyle(self, params={}):
        return 'pcolormesh'
  
#    @apply_to(variable='daily')
    def get_extend(self, params={}):
        return 'neither'

    @apply_to(variable='daily')
    def get_labels(self, params={}):
        return (['No Stress',
                 'Watch',
                 'Warning',
                 'Alert Level 1',
                 'Alert Level 2'],
                [0.5, 1.5, 2.5, 3.5, 4.5])

    @apply_to(variable='outlook')
    def get_labels(self, params={}):
        return (['No Stress',
                 'Watch',
                 'Warning',
                 'Alert Level 1',
                 'Alert Level 2'],
                [0.5, 1.5, 2.5, 3.5, 4.5])

    @apply_to(variable='daily')
    def get_units(self, params={}):
        return ''

    @apply_to(variable='daily')
    def get_contourlines(self, params={}):
        return False

    @apply_to(variable='outlook')
    def get_units(self, params={}):
        return ''

    @apply_to(variable='outlook')
    def get_contourlines(self, params={}):
        return False


    @apply_to(variable='outlook')
    def get_grid(self, params={}, **kwargs):
        """
        Request a Grid object for this dataset.

        Override this method to access grids in a different way.
        """

        gridvar = self.get_variable_mapping(params=params)
        kwargs.update({'depthrange':(0, 2)})
        grid =  CoralGridset(self.get_path(params=params), gridvar, params['period'],
                       prefix=self.get_prefix(params=params),
                       suffix=self.get_suffix(params=params),
                       suffix2=self.get_suffix_prelim(params=params),
                       date=params['date'],
                       **kwargs)
        if params['period'] == '4weeks':
            grid.data = grid.data[0]
        elif params['period'] == '8weeks':
            grid.data = grid.data[1]
        elif params['period'] == '12weeks':
            grid.data = grid.data[2]
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
#
#        grid = self.get_grid(params=args,
#                             lonrange=(lon_min, lon_max),
#                             latrange=(lat_min, lat_max))

        grid = self.get_grid(params=args)

        #extract lat/lon and value
        (lat, lon), (latIndex, lonIndex) = Extractor.getGridPoint(inputLat, inputLon, grid.lats, grid.lons,
                                                     grid.data)
        value = grid.data[latIndex, lonIndex]
        if value is ma.masked:
            raise LandError()
        #return extracted values
        return (lat, lon), value
        
class CoralGridset(Gridset):
 
    def get_filename(self, path, prefix, suffix, date, period):
        """
        Get the latest outlook
        """
#        fileName = os.path.join(path, '*.nc')
#        latestFilePath = max(glob.iglob(fileName), key=os.path.getctime)
#        return latestFilePath
        return getLastestFile(path)

    def load_data(self, variable):
        """
        Load the subset of @variable. Assumes spatial data with layout:
        (time, (depth)), lat, lon

        Override to handle other data layouts.
        """
        try:
            ndim = len(variable.dimensions)
        except AttributeError:
            ndim = variable.ndim

        if ndim == 3:
            # data arranged time, lat, lon
            return variable
        else:
            raise GridWrongFormat()

    def get_depths(self, variables):
        """
        Implement to retrieve the depths for a dataset.
        """
        return np.arange(3) 


class coral(SST):
    DATASET = 'coral'
    PLOTTER = CoralPlotterWrapper

    __periods__ = [
        'daily',
        '4weeks',
        '8weeks',
        '12weeks',
    ]

    __subdirs__ = [
        'daily',
        'outlook',
    ]

    __plots__ = [
        'map',
        'point'
    ]

    __variables__ = [
        'daily',
        'outlook'
    ]

    def process_stats(self, params):
        if params['area'] == 'pac':
            return {}
        else: #params['variable'] == 'outlook' or 'daily' 
            grid = self.plotter.get_grid(params=params) 
            alertLevel = filter_alert(params, grid)
            return {'dial': os.path.join('images', params['variable'] + '_' + str(int(alertLevel)) + '.png')}


def getLastestFile(path):
    """
        Get the latest outlook
    """
    fileName = os.path.join(path, '*.nc')
    #latestFilePath = max(glob.iglob(fileName), key=os.path.getctime)
    latestFilePath = sorted(glob.iglob(fileName), cmp=cmp, key=lambda x: x[-11:-3])
    return latestFilePath[-1] 
