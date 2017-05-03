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
from angleconv import dirflip

from ocean import util, config
from ocean.netcdf import extractor

def slice(haystack, needle, width=5):
    l = bisect.bisect_left(haystack, needle - width)
    r = bisect.bisect_right(haystack, needle + width)

    return (haystack[l:r], l, r)

class WaveWatch3Extraction ():
    """
    Extract wave watch 3 point/rectangular area data.
    """

    serverCfg = None

    _DELTA = 0

    def __init__(self):
        """
        Initialise variables.
        """
        self.serverCfg = config.get_server_config()


    def extract(self, inputLat, inputLon, variableName, month, delta=_DELTA):
        files = glob.glob(self.serverCfg['dataDir']['ww3'] + 'monthly/' +
                          '*%s.nc' % month)
        #sort the files back in time.
        filez = sorted(files, key=lambda filename: filename[-9:-3])
        #align the input lat/lon to grid lat/lon
        xtractor = extractor.Extractor()

        inputLat = float(inputLat)
        inputLon = float(inputLon)

        assert -90 < inputLat < 90

        try:
            assert -180 < inputLon < 180
        except AssertionError:
            if (inputLon > 180):
                inputLon = -180 + (inputLon - 180)
            pass

        nc = Dataset(filez[0], 'r')
        lats, latl, latr = slice(nc.variables['y'], inputLat)
        lons, lonl, lonr = slice(nc.variables['x'], inputLon)

        vari = nc.variables[variableName][:, latl:latr, lonl:lonr]
        (gridLat, gridLon), (gridLatIndex, gridLonIndex) = \
                xtractor.getGridPoint(inputLat, inputLon, lats, lons, vari,
                                      validate_range=False)

        # add the indexes from the sliced array
        gridLatIndex += latl
        gridLonIndex += lonl

        gridValues = []
        latLonValues = []
        timeseries = []
        latsLons = str(gridLat) + ' ' + str(gridLon)
        nc.close()

        # extract the data from the grid point for every file
        for file in filez:
            nc = Dataset(file, 'r')
            var = nc.variables[variableName]
            point = var[:, gridLatIndex, gridLonIndex]
            tvar = nc.variables['time1']
            time = tvar[:]
            timeseries = np.append(timeseries, time)
            gridValues = np.append(gridValues, point)
            nc.close()

        return timeseries, latsLons, latLonValues, gridValues, (gridLat, gridLon)

    def writeOutput(self, fileName, latStr, lonStr, timeseries, dataVals, varStr):
        if varStr == 'Dm':
            label = 'Wave Direction (degrees)'
            dataVals = dirflip(dataVals)
        if varStr == 'Hs':
            label = 'Significant Wave Height (m)'
        if varStr == 'Tm':
            label = 'Wave Period (s)'

        timelabel = 'Date (YYYYMMDD)'
        output = open(fileName, 'w')
        #write lats and lons table header
        output.write('Lat/Lon:' + '\t')
        #for latlon in latsLons:
        output.write(latStr + ' ' + lonStr + '\t')
        output.write('\n')
        output.write(timelabel + '\t')
        output.write(label + '\t')
        output.write('\n')
        for time, point in zip (timeseries, dataVals):
                output.write(str(int(time)) + '\t')
                output.write(str(round(point,2)) + '\t')
                output.write('\n')   
        output.close()
