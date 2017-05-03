#
# (c) 2015 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

import os
import os.path
import sys
import copy
import glob
import json
from datetime import datetime, timedelta

import numpy as np
import numpy.ma as ma

from ocean import util, config
from ocean.config import productName, regionConfig
from ocean.datasets import Dataset
from ww3forecastPlotter import Ww3ForecastPlotter, COMMON_FILES, EXTRA_FILES
from ocean.netcdf import Grid
from ocean.netcdf.extractor import Extractor, LandError



svnDayForecast = '%s_%s.json'

#get the server dependant path configurations
serverCfg = config.get_server_config()

#get dataset dependant production information
ww3Product = productName.products['ww3forecast']

#number of forecast steps
FORECAST_STEPS = 25

class ww3forecast(Dataset):
    PRODUCT_NAME = "Global AUSWAVE Forecast"

    __form_params__ = {
        'mode': str,
        'lat': float,
        'lon': float
    }
    __form_params__.update(Dataset.__form_params__)

    __required_params__ = Dataset.__required_params__ + [
    ]

    __periods__ = [
        '7days',
    ]

    __variables__ = [
        'sig_wav_ht',
        'sig_ht_wnd_sea',
        'sig_ht_sw1',
        'pk_wav_per',
        'wnd_spd',
    ]

    __plots__ = [
        'map',
        'point'
    ]

    __subdirs__ = [
    ]

    def getPlotter(self):
        return Ww3ForecastPlotter()

    def process(self, params):
        response = {}

        varStr = params['variable']
        periodStr = params['period']
        regionStr = params['area']

        '''
            Check whether the data file matches the generated config file.
            If the files match, then just return the config file; otherwise
            process the data file and then return the config file.
        '''

        filename = svnDayForecast % (ww3Product['7d'], '7days')
        configFileName = serverCfg['outputDir'] + filename

        fileName = serverCfg['dataDir']['ww3forecast'] + 'ww3_????????_??.nc'
        latestFilePath = max(glob.iglob(fileName), key=os.path.getctime)

        self.grid = ww3forecastGrid(latestFilePath, latestFilePath, varStr, (-90, 90), (0, 360), (0, FORECAST_STEPS))
        
        self.overlayGrid = ww3forecastGrid(latestFilePath, latestFilePath, self.get_overlay_variable(varStr), (-90, 90), (0, 360), (0, FORECAST_STEPS))

        config = self.generateConfig(latestFilePath, self.grid.time)
        configStr = json.dumps(config) 

#        response['forecast'] = configStr 
#        response['img'] = self.getPlotFileName(varStr, 0, regionStr)[1] + COMMON_FILES['img']
#        response['mapimg'] = self.getPlotFileName(varStr, 0, 'pac')[1] + COMMON_FILES['mapimg']
#        response['scale'] = self.getPlotFileName(varStr, 0, 'pac')[1] + COMMON_FILES['scale']

        if ('mode' in params) and (params['mode'] == 'preprocess'):
            response['preproc'] = 'processing...'
            self.preprocess(varStr, regionStr)
        else:
            if params['plot'] == 'map':
                response['forecast'] = configStr
                response['img'] = self.getPlotFileName(varStr, 0, regionStr)[1] + COMMON_FILES['img']
                response['mapimg'] = self.getPlotFileName(varStr, 0, 'pac')[1] + COMMON_FILES['mapimg']
                response['scale'] = self.getPlotFileName(varStr, 0, 'pac')[1] + COMMON_FILES['scale']
                if varStr == 'wnd_spd':
                    response['map'] = 'wnd'
                    response['arrow'] = self.getPlotFileName(varStr, 0, 'pac')[1] + EXTRA_FILES['map'] + EXTRA_FILES['arrow']
                elif varStr == 'pk_wav_per':
                    response['map'] = 'wav'
                    response['label'] = self.getPlotFileName(varStr, 0, 'pac')[1] + EXTRA_FILES['map'] + EXTRA_FILES['label']
                elif varStr == 'sig_ht_wnd_sea' or varStr == 'sig_ht_sw1':
                    response['map'] = 'height'
                    response['arrow'] = self.getPlotFileName(varStr, 0, 'pac')[1] + EXTRA_FILES['map'] + EXTRA_FILES['arrow']
                else:
                    response['map'] = 'wav'
                    response['arrow'] = self.getPlotFileName(varStr, 0, 'pac')[1] + EXTRA_FILES['map'] + EXTRA_FILES['arrow']

            elif params['plot'] == 'point': #for point value extraction
                (lat, lon), value = self.extract(**params)
                response['value'] = float(value)

        return response

    def batchprocess(self):
        fileName = serverCfg['dataDir']['ww3forecast'] + 'ww3_????????_??.nc'
        latestFilePath = max(glob.iglob(fileName), key=os.path.getctime)
        region = 'pac'

        for varStr in self.__variables__:
            self.grid = ww3forecastGrid(latestFilePath, latestFilePath, varStr, (-90, 90), (0, 360), (0, FORECAST_STEPS))
            self.overlayGrid = ww3forecastGrid(latestFilePath, latestFilePath, self.get_overlay_variable(varStr), (-90, 90), (0, 360), (0, FORECAST_STEPS))

            config = self.generateConfig(latestFilePath, self.grid.time)
            configStr = json.dumps(config)

            if varStr == 'wnd_spd':
                self.grid.data = self.grid.data * 1.94384449

            for step in range(FORECAST_STEPS):
                self.plotSurfaceData(varStr, step, region)
                # self.plot_surface_data(varStr, step, region, config)

            #Generating image for each regions
            for key, value in regionConfig.regions.iteritems():
                if value[0] == 'pac' or value[0] == None:
                    for step in range(FORECAST_STEPS):
                        # self.plotSurfaceData(varStr, step, key)
                        self.plot_surface_data(varStr, step, key, config)

    def preprocess(self, varName, region):
        '''
            Allows the map images to be produced via the URL.
        '''
        cmd = "python " + os.path.dirname(os.path.realpath(__file__)) + "/ww3forecastPreprocess.py"
        os.system(cmd)
#        os.system("python /srv/map-portal/usr/lib/python2.6/site-packages/ocean/datasets/ww3forecast/ww3forecastPreprocess.py")
#        if varName == 'wnd_spd':
#            self.grid.data = self.grid.data * 1.94384449
#        for step in range(FORECAST_STEPS):
#            self.plotSurfaceData(varName, step, region)

    def generateConfig(self, latestFilePath, gridTime):
        '''
            Generate the configuration file
        '''
        baseFileName = os.path.basename(latestFilePath)
        dateTimeValue = baseFileName[4:15]
        baseDateTime = datetime.strptime(dateTimeValue, '%Y%m%d_%H')  
        
        timeArray = gridTime
        timeObjArray = map(timedelta, timeArray)

        dateTimeObjArray = [baseDateTime + x for x in timeObjArray]
        dateTimeStrArray = [{"datetime": x.strftime('%d-%m-%Y %H:%M')} for x in dateTimeObjArray]
        return dateTimeStrArray
   
    def getPlotFileName(self, varName, timeIndex, regionName):
        '''
            A helper method to put together the plot file name.
        '''
        plot_filename = '%s_%s_%s_%02d' % (ww3Product['7d'], varName, regionName, timeIndex)
        plot_filename_fullpath = os.path.join(serverCfg['outputDir'],
                                                  plot_filename)
        raster_filename_fullpath = os.path.join(serverCfg['baseURL'],
                                                 serverCfg['rasterURL'],
                                                 plot_filename)
        return plot_filename_fullpath, raster_filename_fullpath
        

    def plotSurfaceData(self, varName, timeIndex, regionName):
        '''
            Plot wind and wave forecasts dataset, including the following three variables:
            sig_wav_ht, together with the pk_wave_dir vector overlay;
            pk_wav_per, with pk_wav_dir vector overlay;
            and
            wnd_spd, with wnd_dir vector overlay.
        ''' 
        plot_filename_fullpath = self.getPlotFileName(varName, timeIndex, regionName)[0]

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

        plot.plot_basemaps_and_colorbar(self.grid.lats, self.grid.lons, self.grid.data[timeIndex],
                                        overlay_grid = self.overlayGrid.data[timeIndex],
                                        output_filename=plot_filename_fullpath,
                                        units=unitStr, cm_edge_values=cb_ticks,
                                        cb_tick_fmt=cb_tick_fmt,
                                        cb_labels=None, cb_label_pos=None,
                                        cmp_name=cmp_name, extend=extend, clabel=clabel, vector=vector)


        plot.wait()

    def plot_surface_data(self, varName, timeIndex, area, dateTimeStrArray):

        plot_filename_fullpath = self.getPlotFileName(varName, timeIndex, area)[0] + '.png'

        regionLongName = regionConfig.regions[area][2]
        title = regionLongName + '\n'

        params = {}
        params['step'] = timeIndex
        params['forecast'] = dateTimeStrArray
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
        contourLines = plot.get_contourlines(params)
        smoothFactor = plot.get_smooth_fac()
        colors = plot.get_colors(params)
        fill_color = plot.get_fill_color()

        lat_min = regionConfig.regions[area][1]['llcrnrlat']
        lat_max = regionConfig.regions[area][1]['urcrnrlat']
        lon_min = regionConfig.regions[area][1]['llcrnrlon']
        lon_max = regionConfig.regions[area][1]['urcrnrlon']

        
        overlay_grid = self.overlayGrid.data[timeIndex] 
        if varName == 'pk_wav_per':
            overlay_grid = None

        plot.plot_surface_data(self.grid.lats, self.grid.lons, self.grid.data[timeIndex],
                               lat_min, lat_max, lon_min, lon_max,
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
                               extend=extend,
#                               fill_color = fill_color,
                               plotStyle=plotStyle,
                               contourLines=contourLines,
                               contourLabels=clabel, #contourLabels,
                               smoothFactor=smoothFactor,
                               product_label_str=self.PRODUCT_NAME,
                               draw_every=10,
                               area=area,
                               boundaryInUse='False',
                               overlay_grid = overlay_grid) 

        plot.wait()

    def get_overlay_variable(self, variable):
        if variable in ['sig_wav_ht', 'pk_wav_per']:
            return 'mn_wav_dir'
        elif variable in ['sig_ht_wnd_sea']:
            return 'mn_dir_wnd_sea'
        elif variable in ['sig_ht_sw1']:
            return 'mn_dir_sw1'
        elif variable in ['wnd_spd']:
            return 'wnd_dir'
        return ''

    def extract(self, **args):

        area = args['area']
        variable = args['variable']
        inputLat = args['lat']
        inputLon = args['lon']
        step = args['step']

#        lat_min = regionConfig.regions[area][1]['llcrnrlat']
#        lat_max = regionConfig.regions[area][1]['urcrnrlat']
#        lon_min = regionConfig.regions[area][1]['llcrnrlon']
#        lon_max = regionConfig.regions[area][1]['urcrnrlon']

        fileName = serverCfg['dataDir']['ww3forecast'] + 'ww3_????????_??.nc'
        latestFilePath = max(glob.iglob(fileName), key=os.path.getctime)

#        grid = ww3forecastGrid(latestFilePath, latestFilePath, variable, 
#                                    latrange=(lat_min, lat_max), 
#                                    lonrange=(lon_min, lon_max), 
#                                    depthrange=(0, FORECAST_STEPS))

        grid = ww3forecastGrid(latestFilePath, latestFilePath, variable, 
                                    latrange=(-90, 90), 
                                    lonrange=(0, 360), 
                                    depthrange=(0, FORECAST_STEPS))

        if variable == 'wnd_spd':
             grid.data = grid.data * 1.94384449


        #extract lat/lon and value
        step = int(step)
        (lat, lon), (latIndex, lonIndex) = Extractor.getGridPoint(inputLat, inputLon, grid.lats, grid.lons,
                                                     grid.data[step])
        value = grid.data[step][latIndex, lonIndex]

        if value is ma.masked:
            raise LandError()

        #return extracted values
        return (lat, lon), value

class ww3forecastGrid(Grid):
    """
        Inherites class Grid to implement the get_variable method.
    """ 
    TIME_VARIABLE = ['time']
 
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

        if ndim == 4:
            # data arranged time, depth, lat, lon
            return variable[0]
        elif ndim == 3:
            # data arranged time, lat, lon
            return variable[:]
        elif ndim == 2:
            # data arranged lat, lon
            return variable
        else:
            raise GridWrongFormat()
 
        
    def get_depths(self, variables):
        return np.arange(FORECAST_STEPS)
