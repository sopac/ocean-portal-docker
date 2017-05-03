#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import os.path
import numpy as np
import numpy.ma as ma

from ocean import config, util
from ocean.datasets import SST
from ocean.netcdf import SurfacePlotter
from ocean.netcdf.extractor import Extractor, LandError
from ocean.config import regionConfig

serverCfg = config.get_server_config()

class ReynoldsPlotter(SurfacePlotter):
    DATASET = 'reynolds'
    PRODUCT_NAME = "Reynolds SST"

    VARIABLE_MAP = {
        'mean': 'sst',
        'dec': 'sst_dec_cats',
    }

    apply_to = util.Parameterise(SurfacePlotter)

    def get_colormap_strategy(self, params={}):
        return 'nonlinear'

    @apply_to(period='daily')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'daily-new-uncompressed')

    def get_prefix(self, params={}):
        prefix = 'reynolds_sst_avhrr-only-v2_'
        if params['period'] == 'daily':
            prefix = 'avhrr-only-v2.'
        return prefix
 
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
        if value is ma.masked:
            raise LandError()
        #return extracted values
        return (lat, lon), value

class reynolds(SST):
    DATASET = 'reynolds'
    PLOTTER = ReynoldsPlotter

    __periods__ = [
        'daily',
        'monthly',
    ]

    __subdirs__ = [
        'daily-new-uncompressed',
        'averages',
    ]

