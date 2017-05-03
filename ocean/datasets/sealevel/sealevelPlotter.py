#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import csv
import datetime
import shutil
import os.path

import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt

from ocean import config
from ocean.netcdf.extractor import Extractor, LandError
from ocean.netcdf.grid import Grid
from ocean.netcdf.surfaceplotter import SurfacePlotter
from ocean.plotter import getCopyright
from ocean.util.pngcrush import pngcrush
from ocean.config import regionConfig

from tidegauges import TideGauge

serverCfg = config.get_server_config()

# filenames for the respective gridfiles (in datadir/grids/)
GRIDS = {
    'alt': 'jb_ibn_srn_gtn_giy.nc',
    'rec': 'recons_1950_2012_noib_seasrem.nc',

#GAS    'rec': 'recons_1950_2009_noib_seasinc.nc',
}

# start date for the time index in each grid file
REFERENCE_DATE = {
    'alt': datetime.date(1990, 1, 1),
    'rec': datetime.date(1900, 1, 1),
}

class SeaLevelGrid(Grid):
    """
    Load a CMAR dataset using a spatial representation
    """

    def __init__(self, variable, date=None, **kwargs):

        self.date = date
        self.refdate = REFERENCE_DATE[variable]

        filename = os.path.join(serverCfg['dataDir']['sealevel'],
                                'grids',
                                GRIDS[variable])

        Grid.__init__(self, filename, filename, variable, **kwargs)

    def get_days_elapsed(self, date):
        """
        Get the the index of the given date in the data file
        """

        timeElapsed = datetime.date(date.year, date.month, 15) - self.refdate

        return timeElapsed.days

    def get_variable(self, variables, variable):

        # find the index for the requested date
        elapsed = self.get_days_elapsed(self.date)
        time = variables['time'][:]
        time_index = np.where(time == elapsed)[0][0]

        var = Grid.get_variable(self, variables, 'height')

        return var[time_index]

class SeaLevelSeries(SeaLevelGrid):
    """
    Load a CMAR dataset using a temporal representation
    """

    def get_variable(self, variables, variable):

        @np.vectorize
        def timeidx2datetime(time):
            return self.refdate + datetime.timedelta(int(time))

        time = Grid.get_variable(self, variables, 'time')
        self.time = timeidx2datetime(time)

        return Grid.get_variable(self, variables, 'height')

    def get_indexes(self, variable,
                          (lats, (latmin, latmax)),
                          (lons, (lonmin, lonmax)),
                          *args):
        _, (latidx, lonidx) = Extractor.getGridPoint(latmin, lonmin, lats, lons,
                                                     variable[0],
                                                     strategy='exhaustive')

        return (latidx, latidx + 1), (lonidx, lonidx + 1), (0, 0)

    def load_data(self, variable):
        return variable 

    def clip_data(self, variable, (lat_idx1, lat_idx2),
                                  (lon_idx1, lon_idx2),
                                  (depth_idx1, depth_idx2)):

        data = variable[:, lat_idx1, lon_idx1]

        if data[0] is ma.masked:
            raise LandError()

        return data


class SeaLevelSurfacePlotter(SurfacePlotter):
    DATASET = 'sealevel'
#    PRODUCT_NAME = """
#IB not removed; seasonal not removed; global trend not removed; GIA removed
#Data from CSIRO CMAR"""

    def __init__(self, variable):
        super(SeaLevelSurfacePlotter, self).__init__()
        if variable == "rec":
            self.PRODUCT_NAME = """
            IB removed; seasonal cycle removed; global trend not removed; GIA removed
            Data from CSIRO CMAR, Church and White 2009"""
        else:
            self.PRODUCT_NAME = """
            IB not removed; seasonal not removed; global trend not removed; GIA removed
            Data from CSIRO CMAR"""

    def get_colormap_strategy(self, params={}):
        return 'nonlinear'

    def get_grid(self, params={}, **kwargs):
        return SeaLevelGrid(params['variable'], date=params['date'])

    def get_ticks(self, params={}, **kwargs):
        return np.arange(-300,300.01,50.0)

    def get_ticks_format(self, params={}, **kwargs):
        return '%.0f'

    def get_units(self, params={}, **kwargs):
        return 'mm'

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

def plotTidalGauge(outputFilename, saveData=True, **args):
    """
    Plot tidal gauge data
    """

    tidalGaugeId = args['tidalGaugeId']
    tidalGaugeName = args['tidalGaugeName']

    data = TideGauge(tidalGaugeId)

    figure = plt.figure()

    plt.rc('font', size=8)
    plt.title("Monthly sea levels for " + tidalGaugeName)
    plt.ylabel("Sea Level Height (metres)")
    plt.xlabel("Year")

    ax = figure.gca()
    ax.grid(True)

    maxPlot, = ax.plot(data.date, data.maximum, 'r-')
    meanPlot, = ax.plot(data.date, data.mean_, 'k-')
    minPlot, = ax.plot(data.date, data.minimum, 'b-')

    # add legend
    ax.legend([maxPlot, meanPlot, minPlot], ['Max', 'Mean', 'Min'], ncol=3, loc='lower right')

    plt.axhline(y=0, color='k')
    plt.figtext(0.02, 0.02, getCopyright(), fontsize=6)
    plt.figtext(0.90, 0.05, "0.0 = Tidal Gauge Zero",
                fontsize=8, horizontalalignment='right')

    plt.savefig(outputFilename + '.png', dpi=150,
                bbox_inches='tight', pad_inches=.1)

    plt.close()
    pngcrush(outputFilename + '.png')

    with open(outputFilename + '.csv', 'w') as f:

        writer = csv.writer(f)

        writer.writerow(["# Monthly sea levels for " + tidalGaugeName])
        writer.writerow(["# Data from tidalGaugeId"])
        writer.writerow(["# Sea Level Height (metres) relative to Tidal Gauge Zero"])

        writer.writerow(data.headers[1:])

        for row in data:
            writer.writerow(list(row)[1:])

def plotTimeseries(outputFilename, saveData=True, **args):
    """
    Plot altimetry/reconstruction timeseries 
    """
    tidalGaugeName = args["tidalGaugeName"]
    variable = args['variable']
    lat = args['lat']
    lon = args['lon']

    titlePrefix = {
        'alt': "Altimetry",
        'rec': "Reconstruction",
    }[variable]

    grid = SeaLevelSeries(variable,
                          latrange=(lat, lat),
                          lonrange=(lon, lon))

    if saveData:
        with open(outputFilename + ".txt", 'w') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(('# Sea Level %s for %s' % (
                             titlePrefix, tidalGaugeName),))
            if variable == 'alt':
                writer.writerow(['# Corrections: IB not removed; seasonal not removed; global trend not removed; GIA removed'])
                writer.writerow(['# Data from CSIRO CMAR'])
            else:
                writer.writerow(['# Corrections: IB removed; seasonal cycle removed; global trend not removed; GIA removed'])
                writer.writerow(['# Data from CSIRO CMAR, Church and White 2009'])
            writer.writerow(['Date (YYYY-MM)', '%s (mm)' % titlePrefix])

            for date, height in zip(grid.time, grid.data):
                writer.writerow([date.strftime('%Y-%m'), height])

    figure = plt.figure()
    plt.rc('font', size=8)
    plt.title("Sea Level %s for %s" % (titlePrefix, tidalGaugeName))
    plt.ylabel('Sea-Surface Height (mm)')
    plt.xlabel('Year')
    ax = figure.gca()
    ax.grid(True)
    ax.set_ylim(-350, 350)
    ax.plot(grid.time, grid.data, 'b-')
    plt.axhline(y=0, color='k')

    
    if variable == 'alt':
        PRODUCT_NAME = """
        Data from CSIRO CMAR
        IB not removed; seasonal not removed; global trend not removed; GIA removed
        """
    else:
        PRODUCT_NAME = """
        Data from CSIRO CMAR
        IB removed; seasonal cycle removed; global trend not removed; GIA removed
        """

    plt.figtext(0.02, 0.02, getCopyright(), fontsize=6)
    plt.figtext(0.90, 0.02, PRODUCT_NAME.strip(),
                fontsize=6, horizontalalignment='right')

    plt.savefig(outputFilename + ".png", dpi=150,
                bbox_inches='tight', pad_inches=.1)

    plt.close()
    pngcrush(outputFilename + ".png")

    return 0
