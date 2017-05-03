#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Jason Smith <jason.smith@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import os
import os.path
import sys
import copy
import json

from datetime import datetime
from ocean import util, config
from ocean.config import productName, regionConfig
from ocean.netcdf.extractor import Extractor, LandError
from ocean.datasets import Dataset, MissingParameter
from ww3Plotter import Ww3Plotter
from ocean.netcdf import Grid
from ocean.plotter import COMMON_FILES, EXTRA_FILES
from netCDF4 import Dataset as ds
from netCDF4 import num2date

import wavecaller as wc
import formatter as frm
import GridPointFinder as GPF
import ww3ExtA
import numpy as np
import numpy.ma as ma

#Maybe move these into configuration later
pointExt = '%s_%s_%s_%s_%s'
recExt = '%s_%s_%s_%s_%s_%s_%s'

#get the server dependant path configurations
serverCfg = config.get_server_config()

#get dataset dependant production information
ww3Product = productName.products['ww3']

#get the plotter
extractor = ww3ExtA.WaveWatch3Extraction()
getGrid = GPF.Extractor()


#number of forecast steps
FORECAST_STEPS = 744

class ww3(Dataset):
    PRODUCT_NAME = "Global PACCSAP Hindcast"
    VARIABLE_MAP = {    #used for hourly data
        'Hs': 'hs',
        'Tm': 't',
        'hs': 'hs',
        't': 't',
    }

    __form_params__ = {
        'lllat': float,
        'lllon': float,
        'urlat': float,
        'urlon': float,
        'lat' : float,
        'lon' : float
    }
    __form_params__.update(Dataset.__form_params__)

    __required_params__ = Dataset.__required_params__ + [
        'date',
    ]

    __periods__ = [
        'hourly',
        'monthly',
    ]

    __variables__ = [
        'Hs',
        'Tm',
        'Dm',
        'fp',
        'dp',
    ]

    __plots__ = [
        'histogram',
        'waverose',
        'map',
        'point'
    ]

    __subdirs__ = [
        'monthly'
    ]

    def getPlotter(self):
        return Ww3Plotter()

    def process(self, params):
        response = {}

        plot = params['plot']
        if plot == 'map':
            response.update(self.plot_hourly(params))
        elif plot == 'histogram' or plot == 'waverose': #for histogram and waverose
            response.update(self.plot_monthly(params))
        elif plot == 'point':
            response.update(self.extract(**params))
        return response

    def extract(self, **args):
        response = {}
        area = args['area']
        variable = args['variable']
        period = args['period']
        inputLat = args['lat']
        inputLon = args['lon']

        monthNoStr = args['date'].strftime('%m')
        yearStr = args['date'].strftime('%Y')
        dateStr = args['date'].strftime('%d')
        step = int(args['step'])

        if period == 'hourly':
            try:
                variable = self.VARIABLE_MAP[variable]
            except KeyError:
                response['error'] = "The variable %s is not found. " % variable
                return response

            fileName = 'ww3.glob_24m.' + yearStr + monthNoStr + '.nc4'   #ww3.glob_24m.197901.nc4
            filePath = os.path.join(serverCfg['dataDir']['ww3'], period, fileName)

            lat_min = regionConfig.regions[area][1]['llcrnrlat']
            lat_max = regionConfig.regions[area][1]['urcrnrlat']
            lon_min = regionConfig.regions[area][1]['llcrnrlon']
            lon_max = regionConfig.regions[area][1]['urcrnrlon']

            # Get grid from the file
#            grid = ww3Grid(filePath, filePath, variable, (lat_min, lat_max), (lon_min, lon_max), (0, FORECAST_STEPS), params= args)
            grid = ww3Grid(filePath, filePath, variable, (-90, 90), (0, 360), (0, FORECAST_STEPS), params= args)

            #extract lat/lon and value
            (lat, lon), (latIndex, lonIndex) = Extractor.getGridPoint(inputLat, inputLon, grid.lats, grid.lons,
                                                                      grid.data[step])
            value = grid.data[step][latIndex, lonIndex]
            if value is ma.masked:
                raise LandError()
            response['value'] = float(value)
        else:
            response['error'] = "Only hourly data is available. Please choose hourly period."

        return response


    #For hourly surface map
    def plot_hourly(self, params):
        response = {}
        varStr = params['variable']
        periodStr = params['period']
        regionStr = params['area']
        monthNoStr = params['date'].strftime('%m')
        yearStr = params['date'].strftime('%Y')
        dateStr = params['date'].strftime('%d')
        step = int(params['step'])
        fulldateStr = params['date'].strftime('%Y%m%d')

        if periodStr == 'hourly':
            try:
                varStr = self.VARIABLE_MAP[varStr]
            except KeyError:
                response['error'] = "The variable %s is not found. " % varStr
                return response

            fileName = 'ww3.glob_24m.' + yearStr + monthNoStr + '.nc4'   #ww3.glob_24m.197901.nc4
            filePath = os.path.join(serverCfg['dataDir']['ww3'], periodStr, fileName)

            # Get grid from the file
            self.grid = ww3Grid(filePath, filePath, varStr, (-90, 90), (0, 360), (0, FORECAST_STEPS), params= params)
            self.overlayGrid = ww3Grid(filePath, filePath, self.get_overlay_variable(varStr), (-90, 90), (0, 360), (0, FORECAST_STEPS), params= params)

            # Generate forecast
            config = self.generateConfig(filePath, self.grid.time, self.grid.time_units, yearStr, monthNoStr, dateStr)
            self.config = config
            configStr = json.dumps(config)

            # Generate map image and scale
            response['mapimg'] = self.getPlotFileName(varStr, fulldateStr, step, regionStr)[1] + COMMON_FILES['mapimg']
            response['scale'] = self.getPlotFileName(varStr, fulldateStr, step, regionStr)[1] + COMMON_FILES['scale']

            # Generate surface map
            response['img'] = self.getPlotFileName(varStr, fulldateStr, step, regionStr)[1] + COMMON_FILES['img']
            self.plotBasemapAndColourbar(varStr, fulldateStr, step, regionStr)
            self.plotSurfaceData(varStr, fulldateStr, step, regionStr, config)

            response['map'] = 'hs' #varStr
            response['arrow'] = self.getPlotFileName(varStr, fulldateStr, step, regionStr)[1] + EXTRA_FILES['map'] + EXTRA_FILES['arrow']
        else:
            response['error'] = "Only hourly data is available. Please choose hourly period."

        return response

    def get_overlay_variable(self, variable):
        if variable in ['hs', 't']:
            return 'dir'
        return ''

    def plotBasemapAndColourbar(self, varName, fulldateStr, timeIndex, regionName):
        '''
            Plot wind and wave forecasts dataset, including the following three variables:
            sig_wav_ht, together with the pk_wave_dir vector overlay;
            pk_wav_per, with pk_wav_dir vector overlay;
            and
            wnd_spd, with wnd_dir vector overlay.
        '''
        plot_filename_fullpath = self.getPlotFileName(varName, fulldateStr, timeIndex, regionName)[0]

        params = {}
        params['variable'] = varName

        plot = self.getPlotter()

        cmp_name = plot.get_colormap(params)
        unitStr = plot.get_units(params)
        cb_ticks = plot.get_ticks(params)
        cb_tick_fmt = plot.get_ticks_format(params)
        extend = plot.get_extend()
        clabel = plot.get_labels(params)
        vector = plot.get_vector(params)

        self.cm_edge_values = cb_ticks
        self.vector = vector

        plot.plot_basemaps_and_colorbar(self.grid.lats, self.grid.lons, self.grid.data[timeIndex],
                                        overlay_grid = self.overlayGrid.data[timeIndex],
                                        output_filename=plot_filename_fullpath,
                                        units=unitStr, cm_edge_values=cb_ticks,
                                        cb_tick_fmt=cb_tick_fmt,
                                        cb_labels=None, cb_label_pos=None,
                                        cmp_name=cmp_name, extend=extend, clabel=clabel, vector=vector)


        plot.wait()

    def plotSurfaceData(self, varName, fulldateStr, timeIndex, area, dateTimeStrArray):

        plot_filename_fullpath = self.getPlotFileName(varName, fulldateStr, timeIndex, area)[0] + '.png'

        regionLongName = regionConfig.regions[area][2]
        title = regionLongName + '\n'

        params = {}
        params['step'] = timeIndex
        params['forecast'] = dateTimeStrArray[timeIndex]
        params['variable'] = varName

        plot = self.getPlotter()

        formattedDate = plot.get_formatted_date(params)
        title += "%s: %s" % (plot.get_title(params), formattedDate)

        colormap_strategy = plot.get_colormap_strategy(params)
        cmp_name = plot.get_colormap(params)
        units = plot.get_units(params)
        cb_ticks = plot.get_ticks(params)
        cb_tick_fmt = plot.get_ticks_format(params)
        clabel = plot.get_labels(params)
        vector = plot.get_vector(params)

        cb_labels = None
        cb_label_pos = None

        extend = plot.get_extend()
        # contourLabels = plot.get_contour_labels()
        plotStyle = plot.get_plotstyle()
        contourLines = plot.get_contourlines()
        smoothFactor = plot.get_smooth_fac()
        colors = plot.get_colors()
        fill_color = plot.get_fill_color()

        lat_min = regionConfig.regions[area][1]['llcrnrlat']
        lat_max = regionConfig.regions[area][1]['urcrnrlat']
        lon_min = regionConfig.regions[area][1]['llcrnrlon']
        lon_max = regionConfig.regions[area][1]['urcrnrlon']

        plot.plot_surface_data(self.grid.lats, self.grid.lons, self.grid.data[timeIndex],
                               lat_min, lat_max, lon_min, lon_max,
                               overlay_grid = self.overlayGrid.data[timeIndex],
                               output_filename=plot_filename_fullpath ,
                               title=title,
                               units=units,
                               cm_edge_values=cb_ticks,
                               cb_tick_fmt=cb_tick_fmt,
                               cb_labels=cb_labels,
                               cb_label_pos=cb_label_pos,
                               colormap_strategy = colormap_strategy,
                               cmp_name=cmp_name,
                               colors = colors,
                               fill_color = fill_color,
                               extend=extend,
                               plotStyle=plotStyle,
                               contourLines=contourLines,
                               contourLabels=clabel, #contourLabels,
                               smoothFactor=smoothFactor,
                               vector=vector,
                               product_label_str=self.PRODUCT_NAME,
                               area=area,
                               boundaryInUse='False')

        plot.wait()

    def getPlotFileName(self, varName, date, timeIndex, regionName):
        '''
            A helper method to put together the plot file name.
        '''
        plot_filename = '%s_%s_%s_%s_%02d' % (ww3Product['hourly'], varName, regionName, date, timeIndex)
        plot_filename_fullpath = os.path.join(serverCfg['outputDir'],
                                                  plot_filename)
        raster_filename_fullpath = os.path.join(serverCfg['baseURL'],
                                                 serverCfg['rasterURL'],
                                                 plot_filename)
        return plot_filename_fullpath, raster_filename_fullpath

    def generateConfig(self, filePath, times, units, yearStr, monthNoStr, dateStr):
        '''
            Generate the configuration file
        '''
        baseFileName = os.path.basename(filePath)
        dateTimeValue = baseFileName[13:19]
        baseDateTime = datetime.strptime(dateTimeValue, '%Y%m')

        dateTimeObjArray = num2date(times, units, calendar='julian')    #time unit is Julian for the hourly ww3 dataset

        idx= np.where([(d.year == int(yearStr)) & (d.month == int(monthNoStr)) & (d.day == int(dateStr)) for d in dateTimeObjArray])
        dateTimeStrArray = [{"datetime": x.strftime('%d-%m-%Y %H:%M')} for x in dateTimeObjArray[idx]]

        return dateTimeStrArray

    def plot_monthly(self, params):
        response = {}

        if 'lllat' not in params:
            raise MissingParameter("Missing parameter 'lllat'")
        elif 'lllon' not in params:
            raise MissingParameter("Missing parameter 'lllon'")

        varStr = params['variable']
        lllatStr = params['lllat']
        lllonStr = params['lllon']
        urlatStr = params['urlat']
        urlonStr = params['urlon']
        periodStr = params['period']

        month = params['date'].strftime('%m')
        mthStr = params['date'].strftime('%B')

        if lllatStr == urlatStr and lllonStr == urlonStr:
            lats, lons, vari = getGrid.getGridPoint(lllatStr, lllonStr, varStr)
            (latStr,lonStr),(latgrid,longrid) = \
                Extractor.getGridPoint(lllatStr, lllonStr, lats, lons,
                                       vari, strategy='exhaustive',
                                       validate_range=False)
            (latStr, lonStr) = frm.nameformat(latStr, lonStr)
            filename = pointExt % (ww3Product['point'], latStr, lonStr,
                                   varStr, month)
        else:
            (latStr, lonStr) = frm.nameformat(lllatStr, lllonStr)
            filename = recExt % (ww3Product['rect'],
                                 lllatStr, lllonStr,
                                 urlatStr, urlonStr,
                                 varStr, month)

        outputFileName = serverCfg['outputDir'] + filename

        timeseries = None

        if not os.path.exists(outputFileName + '.txt'):
            timeseries, latsLons, latLonValues, gridValues, \
                (gridLat, gridLon) = extractor.extract(lllatStr, lllonStr,
                                                       varStr, month)

            dataVals = copy.copy(gridValues)
            extractor.writeOutput(outputFileName + '.txt',
                                  latStr, lonStr, timeseries, dataVals, varStr)

        if not os.path.exists(outputFileName + '.txt'):
            response['error'] = "Error occured during the extraction."
        else:
            response['ext'] = os.path.join(serverCfg['baseURL'],
                                           serverCfg['rasterURL'],
                                           filename + '.txt')
            os.utime(os.path.join(serverCfg['outputDir'], filename + '.txt'),
                     None)

        if not os.path.exists(outputFileName + ".png"):
            if timeseries is None:
                # only reload the data if we have to
                timeseries, latsLons, latLonValues, gridValues, \
                    (gridLat, gridLon) = extractor.extract(lllatStr, lllonStr,
                                                           varStr, month)
            wc.wavecaller(outputFileName, varStr,
                          gridLat, gridLon, lllatStr, lllonStr,
                          gridValues, mthStr)

        if os.path.exists(outputFileName + '.png'):
            response['img'] = os.path.join(serverCfg['baseURL'],
                                           serverCfg['rasterURL'],
                                           filename + '.png')
            os.utime(os.path.join(serverCfg['outputDir'], filename + '.png'),
                     None)

        return response

class ww3Grid(Grid):

    # a list of possible variables for latitudes
    LATS_VARIABLE = ['latitude']

    # a list of possible variables for longitude
    LONS_VARIABLE = ['longitude']

    #time variable name
    TIME_VARIABLE = ['time']

    def load_data(self, variable):
        """
        Load the subset of @variable. Assumes spatial data with layout:
        (time, (depth)), lat, lon

        Override to handle other data layouts.
        """

        if (self.params):
            periodStr = self.params['period']
            if (periodStr == 'hourly'):
                yearStr = self.params['date'].strftime('%Y')
                monthNoStr = self.params['date'].strftime('%m')
                dateStr = self.params['date'].strftime('%d')
                dateTimeObjArray = num2date(self.time, self.time_units, calendar='julian')    #time unit is Julian for the hourly ww3 dataset
                idx= np.where([(d.year == int(yearStr)) & (d.month == int(monthNoStr)) & (d.day == int(dateStr)) for d in dateTimeObjArray])
                self.idx = idx
        try:
            ndim = len(variable.dimensions)
        except AttributeError:
            ndim = variable.ndim

        if ndim == 4:
            # data arranged time, depth, lat, lon
            return variable[0]
        elif ndim == 3:
            # data arranged time, lat, lon
            idx_list_start = idx[0][0]
            idx_list_end = idx_list_start + len(idx[0].tolist()) + 1
            if (idx):   #for hourly data
                return variable[idx_list_start: idx_list_end]
            else:
                return variable[:]
        elif ndim == 2:
            # data arranged lat, lon
            return variable
        else:
            raise GridWrongFormat()

    def get_depths(self, variables):
        return np.arange(FORECAST_STEPS)
