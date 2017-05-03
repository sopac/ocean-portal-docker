#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Jason Smith <jason.smith@bom.gov.au>

import glob
import bisect
import math

import numpy as np
from netCDF4 import Dataset

from ocean import config

class Extractor ():
    """
    Extract point/rectangular area data.
    """

    def __init__(self):
        """
        Initialise variables.
        """
        self.serverCfg = config.get_server_config()

    def getGridPoint(self, inputLat, inputLon, varStr):
        """
        Align the input lat/lon to the grid lat/lon. Also returns the index of the grid lat/lon.
        """
        file = glob.glob(self.serverCfg["dataDir"]["ww3"] + 'monthly/' +
                         'ww3_outf_1979??.nc')
        nc = Dataset(file[0], 'r')
        lats  = nc.variables['y'][:] 
        lons = nc.variables['x'][:]
        var = nc.variables[varStr][:][0]

        return lats, lons, var

    def extract(self, data, lats, lons, latTop, latBottom, lonLeft, lonRight):
        """
        Extract an area of data from the gridded data.
        """
        latmin = lats >= latBottom
        latmax = lats <= latTop
        lonmin = lons >= lonLeft
        lonmax = lons <= lonRight

        latrange = latmin & latmax
        lonrange = lonmin & lonmax 

        latSlice = sst[latrange]
        extracted = latSlice[:, lonrange]
        return extracted
