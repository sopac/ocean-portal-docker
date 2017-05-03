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
from ocean.config import productName
from ocean.config import regionConfig 
from ocean.datasets import Dataset
from currentforecastPlotter import CurrentForecastPlotter, COMMON_FILES, EXTRA_FILES
from ocean.netcdf import Grid
from ocean.netcdf.extractor import Extractor, LandError

svnDayForecast = '%s_%s.json'

#get the server dependant path configurations
serverCfg = config.get_server_config()

#get dataset dependant production information
currentProduct = productName.products['currentfc']

#number of forecast steps
FORECAST_STEPS = 12 

class currentforecast(Dataset):
    PRODUCT_NAME = "Forecast Surface Currents"

    __form_params__ = {
        'mode': str,
        'lat': float,
        'lon': float
    }
    __form_params__.update(Dataset.__form_params__)

    __required_params__ = Dataset.__required_params__ + [
    ]

    __periods__ = [
        '3days'
    ]

    __variables__ = [
        'currents'
    ]

    __plots__ = [
        'map',
        'point'
    ]

    __subdirs__ = [
    ]

    def getPlotter(self):
        return CurrentForecastPlotter()

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
        filename = svnDayForecast % (currentProduct['7d'], '7days')
        configFileName = serverCfg['outputDir'] + filename

        latestFilePath = serverCfg['dataDir']['currents'] + 'daily/latest_HYCOM_currents.nc'

        if not os.path.exists(configFileName):
            #The grid where u and v have been converted to magnitude
            self.grid = currentforecastGrid(latestFilePath, latestFilePath, ('u', 'v'), (-90, 90), (105, 295), (0, FORECAST_STEPS))
            #Generate the config file
            config = self.generateConfig(latestFilePath, self.grid.time)
            with open(configFileName, 'w') as f:
                json.dump(config, f)
        else:
            with open(configFileName, 'r') as f:
                config = json.load(f)
        configStr = json.dumps(config) 


        if ('mode' in params) and (params['mode'] == 'preprocess'):
            response['preproc'] = 'being processed...'
            self.preprocess(varStr, regionStr)
        else:
            if params['plot'] == 'map':
                response['forecast'] = configStr 
                response['mapimg'] = self.getPlotFileName(varStr, 0, regionStr)[1] + COMMON_FILES['mapimg']
                response['img'] = self.getPlotFileName(varStr, 0, regionStr)[1] + COMMON_FILES['img']
                response['scale'] = self.getPlotFileName(varStr, 0, regionStr)[1] + COMMON_FILES['scale']
                response['map'] = 'current'
                response['arrow'] = self.getPlotFileName(varStr, 0, regionStr)[1] + EXTRA_FILES['map'] + EXTRA_FILES['arrow']
            elif params['plot'] == 'point': #for point value extraction
                (lat, lon), value = self.extract(**params)
                response['value'] = float(value)


        return response

    def batchprocess(self):
        filename = svnDayForecast % (currentProduct['7d'], '7days')
        configFileName = serverCfg['outputDir'] + filename
        latestFilePath = serverCfg['dataDir']['currents'] + 'daily/latest_HYCOM_currents.nc'

        self.grid = currentforecastGrid(latestFilePath, latestFilePath, ('u', 'v'), (-90, 90), (105, 295), (0, FORECAST_STEPS))
        #Generate configuration file
        config = self.generateConfig(latestFilePath, self.grid.time)
        with open(configFileName, 'w') as f:
            json.dump(config, f)

        varName = "currents"

        for key, value in regionConfig.regions.iteritems():
            if value[0] == 'pac' or value[0] == None:
                for step in range(FORECAST_STEPS):
                    self.plotSurfaceData(varName, step, key)
                    self.plot_surface_data(varName, step, key, config)

    def preprocess(self, varName, region):
        '''
            Allows the map images to be produced via the URL.
        '''
        cmd = "python " + os.path.dirname(os.path.realpath(__file__)) + "/currentPreprocess.py"
        os.system(cmd)
#        os.system("python /srv/map-portal/usr/lib/python2.6/site-packages/ocean/datasets/currentforecast/currentPreprocess.py")
#        for step in range(FORECAST_STEPS):
#            self.plotSurfaceData(varName, step, region) 
#        self.plotSurfaceData(varName, 0, region) 

    def generateConfig(self, latestFilePath, gridTime):
        '''
            Generate the configuration file
        '''
        baseDateTime = datetime(2000, 1, 1, 0, 0, 0)

        timeArray = gridTime
        timeObjArray = map(lambda(x): timedelta(hours=+x), timeArray.astype(float))

        dateTimeObjArray = [baseDateTime + x for x in timeObjArray]
        dateTimeStrArray = [{"datetime": x.strftime('%d-%m-%Y %H:%M')} for x in dateTimeObjArray]
        return dateTimeStrArray

    def getPlotFileName(self, varName, timeIndex, regionName):
        '''
            A helper method to put together the plot file name.
        '''
        plot_filename = '%s_%s_%s_%02d' % (currentProduct['7d'], 'current', regionName, timeIndex)
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
        plot = self.getPlotter()

        cm = plot.get_colormap()
        cb_ticks = plot.get_ticks()
        unitStr = plot.get_units()
        cb_tick_fmt = plot.get_ticks_format()
        plot_filename_fullpath = self.getPlotFileName(varName, timeIndex, regionName)[0]
        clabel = False
        vector = True
        extend = plot.get_extend()

        plot.plot_basemaps_and_colorbar(self.grid.lats, self.grid.lons, self.grid.data, timeIndex, 
        #                                overlay_grid = self.overlayGrid.data[timeIndex],
                                        output_filename=plot_filename_fullpath,
                                        units=unitStr, cm_edge_values=cb_ticks,
                                        cb_tick_fmt=cb_tick_fmt,
                                        cb_labels=None, cb_label_pos=None,
                                        cmp_name=cm, extend=extend, clabel=clabel, vector=vector, regionName = regionName)


        plot.wait()

    def plot_surface_data(self, variable, timeIndex, area, dateTimeStrArray):

        output_filename = self.getPlotFileName(variable, timeIndex, area)[0] + '.png'

        regionLongName = regionConfig.regions[area][2]
        title = regionLongName + '\n'

        params = {}
        params['step'] = timeIndex
        params['forecast'] = dateTimeStrArray

        plot = self.getPlotter()

        formattedDate = plot.get_formatted_date(params)
        title += "%s: %s" % ('Current speed and Direction', formattedDate)

        cmap_name = plot.get_colormap()
        cb_ticks = plot.get_ticks()
        units = plot.get_units()
        cb_tick_fmt = plot.get_ticks_format()
        cb_labels = None

        cb_label_pos = plot.get_labels()

        extend = plot.get_extend()
        contourLabels = plot.get_contour_labels()
        plotStyle = plot.get_plotstyle()
        contourLines = plot.get_contourlines()
        smoothFactor = plot.get_smooth_fac()
        colors = plot.get_colors()
        fill_color = plot.get_fill_color()
        colormap_strategy = plot.get_colormap_strategy()

        lat_min = regionConfig.regions[area][1]['llcrnrlat']
        lat_max = regionConfig.regions[area][1]['urcrnrlat']
        lon_min = regionConfig.regions[area][1]['llcrnrlon']
        lon_max = regionConfig.regions[area][1]['urcrnrlon']

        plot.plot_surface_data(self.grid.lats, self.grid.lons, self.grid.data, timeIndex,
                               lat_min, lat_max, lon_min, lon_max,
                               output_filename=output_filename,
                               title=title,
                               units=units,
                               cm_edge_values=cb_ticks,
                               cb_tick_fmt=cb_tick_fmt,
                               cb_labels=cb_labels,
                               cb_label_pos=cb_label_pos,
                               colormap_strategy = colormap_strategy,
                               cmp_name=cmap_name,
                               colors = colors,
                               fill_color = fill_color,
                               extend=extend,
                               plotStyle=plotStyle,
                               contourLines=contourLines,
                               contourLabels=contourLabels,
                               smoothFactor=smoothFactor,
                               product_label_str=self.PRODUCT_NAME,
                               area=area,
                               boundaryInUse='False')

        plot.wait()

    def get_overlay_variable(self, variable):
        if variable in ['sig_wav_ht', 'sig_ht_wnd_sea', 'sig_ht_sw1',  'pk_wav_per']:
            return 'mn_wav_dir'
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

        latestFilePath = serverCfg['dataDir']['currents'] + 'daily/latest_HYCOM_currents.nc'
        grid = currentforecastGrid(latestFilePath, latestFilePath, ('u', 'v'), (-90, 90), (105, 295), (0, FORECAST_STEPS))

        #extract lat/lon and value
        step = int(step)
        u = grid.data[0][step]
        v = grid.data[1][step]
        mag = np.sqrt(u**2 + v**2)
        (lat, lon), (latIndex, lonIndex) = Extractor.getGridPoint(inputLat, inputLon, grid.lats, grid.lons,
                                                     mag)
        value = mag[latIndex, lonIndex]

        if value is ma.masked:
            raise LandError()

        #return extracted values
        return (lat, lon), value

class currentforecastGrid(Grid):
    """
        Inherites class Grid to implement the  method.
    """ 
    TIME_VARIABLE = ['time']

    def get_variable(self, variables, variable):
        """
        Retrieve @variable
        variable is a tuple consisting of u and v.
        """

        try:
            return variables[variable[0]], variables[variable[1]]
        except KeyError as e:
            raise GridWrongFormat(e)
 
    def load_data(self, variable):
        """
        Load the subset of @variable. Assumes spatial data with layout:
        (time, (depth)), lat, lon

        variable is a tuple consisting of u and v.

        Override to handle other data layouts.
        """

        try:
            ndim = len(variable[0].dimensions)
        except AttributeError:
            ndim = variable.ndim

        if ndim == 4:
            # data arranged time, depth, lat, lon
            return variable[0]
        elif ndim == 3:
            # data arranged time, lat, lon
            return variable[0][:], variable[1][:]
        elif ndim == 2:
            # data arranged lat, lon
            return variable
        else:
            raise GridWrongFormat()
 
    def clip_data(self, data, (lat_idx1, lat_idx2),
                                  (lon_idx1, lon_idx2),
                                  (depth_idx1, depth_idx2)):
        ndim = len(data[0].shape)
        if ndim == 3:
            return data[0][depth_idx1:depth_idx2,
                            lat_idx1:lat_idx2:self.GRID_SPACING,
                            lon_idx1:lon_idx2:self.GRID_SPACING], \
                   data[1][depth_idx1:depth_idx2,
                            lat_idx1:lat_idx2:self.GRID_SPACING,
                            lon_idx1:lon_idx2:self.GRID_SPACING] 
        elif ndim == 2:
            return data[lat_idx1:lat_idx2:self.GRID_SPACING,
                        lon_idx1:lon_idx2:self.GRID_SPACING]
        else:
            raise GridWrongFormat()

    def get_depths(self, variables):
        return np.arange(FORECAST_STEPS)
#        return [0]
