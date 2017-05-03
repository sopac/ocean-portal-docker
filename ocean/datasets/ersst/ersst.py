#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Matthew Howie
#          Danielle Madeley <d.madeley@bom.gov.au>

import os.path
import numpy as np
import numpy.ma as ma

from ocean import config
from ocean.datasets import SST
from ocean.netcdf import SurfacePlotter
from ocean.util import Parameterise
from ocean.netcdf.extractor import Extractor, LandError
from ocean.config import regionConfig

serverCfg = config.get_server_config()

class ERSSTPlotter(SurfacePlotter):

    DATASET = 'ersst'
    PRODUCT_NAME = "Extended Reconstructed SST"

    VARIABLE_MAP = {
        'mean': 'sst',
        'dec': 'sst_dec_cats',
    }

    apply_to = Parameterise(SurfacePlotter)

#    @apply_to()
#    def get_prefix(self, params={}):
#        return 'ersst_v3b_'
#
#    @apply_to(period='monthly')
#    def get_prefix(self, params={}):
#        return 'ersst.'

    def get_prefix(self, params={}):
        prefix = 'ersst_v3b_'
        if params['period'] == 'monthly': 
            prefix = 'ersst.'
        return prefix

    @apply_to(period='monthly')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET], 'monthly')

    @apply_to(period='monthly', variable='dec')
    def get_path(self, params={}):
        return self.get_path(params=params, _ignore=['period'])

    def get_colormap_strategy(self, params={}):
        return 'nonlinear'

    @apply_to(variable='dec')
    def get_plotstyle(self, params={}):
        return 'pcolormesh'

    def get_plotstyle(self, params={}):
        return 'contourf'

    @apply_to(variable='dec')
    def get_contourlines(self, params={}):
        return False

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
  
class ersst(SST):
    DATASET = 'ersst'
    PLOTTER = ERSSTPlotter

    __periods__ = [
        'monthly',
        '3monthly',
        '6monthly',
        '12monthly',
        'yearly',
    ]

    __subdirs__ = [
        'monthly',
        'averages',
        'decile',
    ]
