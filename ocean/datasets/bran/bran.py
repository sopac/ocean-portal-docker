#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Nick Summons <n.summons@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import os
import os.path
import sys
import datetime

import numpy as np
import numpy.ma as ma

from ocean import util, config, logger
from ocean.config import regionConfig, productName
from ocean.plotter import Plotter, COMMON_FILES
from ocean.datasets import Dataset
from ocean.util import dateRange
from ocean.netcdf.extractor import Extractor, LandError

import branPlotterNew

server_config = config.get_server_config()
branProduct = productName.products['bran']

BRAN_VERSION = 'bran3.5'
PRODUCT_LABEL = 'Bluelink Reanalysis 3.5'

class bran(Dataset):

    __form_params__ = {
        'lat': np.float,
        'lon': np.float,
    }
    __form_params__.update(Dataset.__form_params__)

    __variables__ = [
        'temp',
        'salt',
        'eta',
        'uv',
        'uveta',
    ]

    __periods__ = [
        'monthly',
        '3monthly',
        '6monthly',
        '12monthly',
    ]

    __required_params__ = Dataset.__required_params__ + [
        'date',
        'area',
    ]

    __plots__ = [
        'map',
        'xsections',
        'point'
    ]

    __subdirs__ = [
        'monthly',
        'averages',
    ]

    def process(self, params):
        response = {}

        varName = params['variable']
        regionStr = params['area']
        periodStr = params['period']
        inputDate = params["date"]
        date = inputDate.strftime('%Y%m%d')
        yearStr = '%04i' % inputDate.year
        monthStr = '%02i' % inputDate.month
        yearMonthStr = yearStr + monthStr


        if params['plot'] == 'point': #for point value extraction
            (lat, lon), value = extract(**params)
            response['value'] = float(value)
            return response
        elif params['plot'] == 'xsections':
#        if ('lat' in params) and ('lon' in params):
#            plot_subsurface = True
            # Display error if variable selected for subsurface plot is invalid
            if not (varName == 'temp' or varName == 'salt'):
                response['error'] = "To display a depth cross section, please select either Temperature or Salinity variables."
                return response
#        else:
#            plot_subsurface = False

#        if plot_subsurface:
            lat_cnt = params['lat']
            lon_cnt = np.mod(params['lon'], 360.0)

            if (0 <= lon_cnt <= 360) and (-90 <= lat_cnt <= 90):
                lon_str = '%.2fE' % lon_cnt
                if lat_cnt >= 0:
                    lat_str = '%.2fN' % lat_cnt
                else:
                    lat_str = '%.2fS' % abs(lat_cnt)

                regionStr = '%s_%s' % (lat_str, lon_str)
                regionStr = regionStr.replace('.', '')
            else:
                response['error'] = "Invalid lat/lon coordinates"
                return response

            plot_filename = '%s_%s_%s_%s' % (branProduct[periodStr],
                                             varName, yearMonthStr, regionStr)
            plot_filename_fullpath = os.path.join(server_config['outputDir'],
                                                  plot_filename)
            basemap_filename = '%s_%s_%s' % (branProduct[periodStr],
                                             varName, yearMonthStr)
            basemap_filename_fullpath = os.path.join(server_config['outputDir'],
                                                     basemap_filename)

            # Generate basemap if does not exist
            if not check_basemap_exists(basemap_filename_fullpath):
                plot_surface_data(varName, date, periodStr, yearStr, monthStr, regionStr,
                                  basemap_filename_fullpath, basemap_only=True)

            # Determine plot settings
            if varName == 'temp':
                unitStr = ur'\u00b0' + 'C'
                varLongName = 'Surface and Subsurface Temperature Profile'
                cb_ticks = np.arange(16.0, 30.1, 1.0)
            elif varName == 'salt':
                unitStr = 'PSU'
                varLongName = 'Surface and Subsurface Salinity Profile'
                cb_ticks = np.arange(33, 37.1, 0.5)

            # Load sub-surface data
            if periodStr == 'monthly':
                title_date_str = params['date'].strftime('%B %Y')
                input_data_file = os.path.join(server_config['dataDir']['bran'],
                                              periodStr, varName,
                                              '%s_%s_%s.nc4' % (varName,
                                                                yearStr,
                                                                monthStr))
            else:
                # FIXME: this is horrific
                monthInt = int(''.join(i for i in periodStr if i.isdigit()))
                months = dateRange.getMonths(date, monthInt)
                title_date_str = months[0].strftime('%B %Y') + ' to ' + months[-1].strftime('%B %Y')
                input_data_file = os.path.join(server_config['dataDir']['bran'],
                                              'averages', periodStr, varName,
                                              BRAN_VERSION + '_%smthavg_%s_%s.nc4' % (monthInt, months[0].strftime('%Y%m'), months[-1].strftime('%Y%m')))
            titleStr = varLongName + ': \n' + title_date_str + '\n'

            lats1, lons1, zlevels1, zonal_data = \
                branPlotterNew.load_BRAN_data(input_data_file, varName,
                                              lat_cnt, lat_cnt,
                                              lon_cnt - 5.0, lon_cnt + 5.0,
                                              depth_min=0.0, depth_max=300.0)
            lats2, lons2, zlevels2, meridional_data = \
                branPlotterNew.load_BRAN_data(input_data_file, varName,
                                              lat_cnt - 5.0, lat_cnt + 5.0,
                                              lon_cnt, lon_cnt,
                                              depth_min=0.0, depth_max=300.0)

            # Load surface data
            lats, lons, zlevels, data = \
                branPlotterNew.load_BRAN_data(input_data_file, varName,
                                              -999.0, 999.0, -999.0, 999.0)

            # Generate subsurface plot
            branPlotterNew.plot_BRAN_depth_slice(zlevels1, lats2, lons1,
                                                 zonal_data, meridional_data,
                                                 lats, lons, data,
                                                 lat_cnt, lon_cnt,
                                                 output_filename=plot_filename_fullpath + '.png',
                                                 units=unitStr, title=titleStr,
                                                 cb_ticks=cb_ticks,
                                                 product_label_str=PRODUCT_LABEL)
        elif params['plot'] == 'map':
            # Plot surface data
            plot_filename = '%s_%s_%s_%s' % (branProduct[periodStr],
                                             varName, yearMonthStr, regionStr)
            plot_filename_fullpath = os.path.join(server_config['outputDir'],
                                                  plot_filename)
            basemap_filename = plot_filename
            basemap_filename_fullpath = plot_filename_fullpath

            if not check_basemap_and_plot_exists(plot_filename_fullpath):
                # If drawing currents, determine vector plot settings
                if varName in ['uv', 'uveta']:
                    lat_min = regionConfig.regions[regionStr][1]['llcrnrlat']
                    lat_max = regionConfig.regions[regionStr][1]['urcrnrlat']
                    lon_min = regionConfig.regions[regionStr][1]['llcrnrlon']
                    lon_max = regionConfig.regions[regionStr][1]['urcrnrlon']

                    draw_every, arrow_scale = \
                        branPlotterNew.get_vector_plot_settings(lat_min,
                                                                lat_max,
                                                                lon_min,
                                                                lon_max)

                    # Display error if chosen region is too large for
                    # displaying currents
                    if (draw_every is None) or (arrow_scale is None):
                        response['error'] = "The region is too large for displaying currents.  Please select a smaller region and try again."
                        return response
                else:
                    draw_every, arrow_scale = None, None

                plot_surface_data(varName, date, periodStr, yearStr, monthStr, regionStr,
                                  basemap_filename_fullpath,
                                  plot_filename_fullpath=plot_filename_fullpath,
                                  basemap_only=False, draw_every=draw_every,
                                  arrow_scale=arrow_scale)

        if check_basemap_exists(basemap_filename_fullpath) and \
           check_plot_exists(plot_filename_fullpath):

            response.update(util.build_response_object(
                            COMMON_FILES.keys(),
                            os.path.join(server_config['baseURL'],
                                         server_config['rasterURL'],
                                         basemap_filename),
                            COMMON_FILES.values()))
            response['img'] = os.path.join(server_config['baseURL'],
                                           server_config['rasterURL'],
                                           plot_filename + '.png')
            if params['variable'] == 'temp':
                if regionConfig.regions[params['area']][0] == 'pac':
                    response['map'] = 'mean_sub'
                else:
                    response['map'] = 'mean'
            elif params['variable'] == 'salt':
                response['map'] = 'salt'
            elif params['variable'] == 'uv':
                response['map'] = 'uv'

            util.touch_files(os.path.join(server_config['outputDir'],
                                          plot_filename),
                             COMMON_FILES.values())
            util.touch_files(os.path.join(plot_filename_fullpath),
                             [ COMMON_FILES['img'] ])
        else:
            response['error'] = "Requested image is not available at this time."

        return response

@logger.time_and_log
def plot_surface_data(varName, date, periodStr, yearStr, monthStr, regionStr,
                      basemap_filename_fullpath,
                      plot_filename_fullpath=None, basemap_only=False,
                      draw_every=1, arrow_scale=10):

    extend = 'both'
    plotStyle='contourf'

    if varName == 'temp':
        dataVar = 'temp'
        unitStr = ur'\u00b0' + 'C'

        if regionStr in regionConfig.regions:
            if regionConfig.regions[regionStr][0] == 'pac':
                cb_ticks = np.arange(20.0, 32.1, 1.0)
            else:
                cb_ticks = np.arange(0.0, 32.1, 2.0)
        else:
            cb_ticks = np.arange(0.0, 32.1, 2.0)

        varLongName = "Sea Surface Temperature"
        cb_tick_fmt = '%.0f'
        currents = False
    elif varName == 'uv':
        dataVar = 'u'
        unitStr = 'm/s'
        cb_ticks = np.array([0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 1.0, 1.5, 2.5])
        varLongName = "Currents Speed and Direction"
        cb_tick_fmt = '%.2f'
        currents = True
        extend = 'neither'
        draw_every = 5
        plotStyle='pcolormesh'
    elif varName == 'salt':
        dataVar = 'salt'
        unitStr = "PSU"
        cb_ticks = np.arange(33, 37.1, 0.5)
        varLongName = "Sea Surface Salinity"
        cb_tick_fmt = '%.1f'
        currents = False
    elif varName == 'eta':
        dataVar = 'eta'
        unitStr = "Metres"
        cb_ticks = np.arange(-0.5, 0.51, 0.1)
        varLongName = "Sea Level Height"
        cb_tick_fmt = '%.2f'
        currents = False
    elif varName == 'uveta':
        dataVar = 'eta'
        unitStr = "Metres"
        cb_ticks = np.arange(-0.3, 0.31, 0.06)
        varLongName = "Sea Level Height and Currents"
        cb_tick_fmt = '%.2f'
        currents = True

    # Load surface data
    if periodStr == 'monthly':
        title_date_str = datetime.date(int(yearStr), int(monthStr), 1).strftime('%B %Y')
        input_data_file = os.path.join(server_config['dataDir']['bran'],
                                      periodStr, dataVar,
                                      '%s_%s_%s.nc4' % (dataVar,
                                                        yearStr,
                                                        monthStr))
    else:
        monthInt = int(''.join(i for i in periodStr if i.isdigit()))
        months = dateRange.getMonths(date, monthInt)
        title_date_str = months[0].strftime('%B %Y') + ' to ' + months[-1].strftime('%B %Y')
        input_data_file = os.path.join(server_config['dataDir']['bran'],
                                      'averages', periodStr, dataVar,
                                      BRAN_VERSION + '_%smthavg_%s_%s.nc4' % (monthInt, months[0].strftime('%Y%m'), months[-1].strftime('%Y%m')))

    lats, lons, zlevels, data = \
        branPlotterNew.load_BRAN_data(input_data_file, dataVar,
                                      -999.0, 999.0, -999.0, 999.0)

    # Plot background image layers
    plot = Plotter()
    if varName not in ['uv']:
        plot.plot_basemaps_and_colorbar(lats, lons, data,
                                    output_filename=basemap_filename_fullpath,
                                    units=unitStr, cm_edge_values=cb_ticks,
                                    cb_tick_fmt=cb_tick_fmt,
                                    cb_labels=None, cb_label_pos=None,
                                    cmp_name='jet', extend=extend, fill_color='0.02')

    if not basemap_only:
        # Get domain boundaries
        lat_min = regionConfig.regions[regionStr][1]['llcrnrlat']
        lat_max = regionConfig.regions[regionStr][1]['urcrnrlat']
        lon_min = regionConfig.regions[regionStr][1]['llcrnrlon']
        lon_max = regionConfig.regions[regionStr][1]['urcrnrlon']

        # Construct title
        regionLongName = regionConfig.regions[regionStr][2]
        title = regionLongName + '\n' + varLongName + ': ' + title_date_str

        lats, lons, zlevels, data = \
            branPlotterNew.load_BRAN_data(input_data_file, dataVar,
                                          lat_min, lat_max,
                                          lon_min, lon_max)

        # Load current data if required
        if currents == True or varName in ['uv']: # For 'uv' variable we need to read from multiple input files.
            if varName not in ['uv']:
                lat_min = lat_min - 1.0
                lat_max = lat_max + 1.0
                lon_min = lon_min - 1.0
                lon_max = lon_max + 1.0

            if periodStr == 'monthly':
                input_data_file = os.path.join(server_config['dataDir']['bran'],
                                               periodStr, 'u',
                                               'u_%s_%s.nc4' % (yearStr, monthStr))
            else:
                input_data_file = os.path.join(server_config['dataDir']['bran'],
                                               'averages', periodStr, 'u',
                                               BRAN_VERSION + '_%smthavg_%s_%s.nc4' % (monthInt, months[0].strftime('%Y%m'), months[-1].strftime('%Y%m')))
            lats2, lons2, zlevels, u = \
                branPlotterNew.load_BRAN_data(input_data_file, 'u',
                                              lat_min, lat_max,
                                              lon_min, lon_max)
            if periodStr == 'monthly':
                input_data_file = os.path.join(server_config['dataDir']['bran'],
                                               periodStr, 'v',
                                               'v_%s_%s.nc4' % (yearStr, monthStr))
            else:
                input_data_file = os.path.join(server_config['dataDir']['bran'],
                                               'averages', periodStr, 'v',
                                               BRAN_VERSION + '_%smthavg_%s_%s.nc4' % (monthInt, months[0].strftime('%Y%m'), months[-1].strftime('%Y%m')))
            lats2, lons2, zlevels, v = \
                branPlotterNew.load_BRAN_data(input_data_file, 'v',
                                              lat_min, lat_max,
                                              lon_min, lon_max)
            contourLines = False

        else:
            lats2 = None; lons2 = None
            u = None; v = None
            contourLines = True

        if varName in ['uv']:
            data = np.sqrt(u**2 + v**2)
            #Plot basemap
            plot.plot_basemaps_and_colorbar(lats, lons, data,
                                    output_filename=basemap_filename_fullpath,
                                    units=unitStr, cm_edge_values=cb_ticks,
                                    cb_tick_fmt=cb_tick_fmt,
                                    cb_labels=None, cb_label_pos=None,
                                    cmp_name='jet', extend=extend, fill_color='0.02')
                                    #cmp_name='jet', extend=extend, fill_color='0.85')

        # Plot surface data
        plot.plot_surface_data(lats, lons, data,
                               lat_min, lat_max, lon_min, lon_max,
                               output_filename=plot_filename_fullpath + '.png',
                               title=title, units=unitStr,
                               cm_edge_values=cb_ticks, cb_tick_fmt=cb_tick_fmt,
                               cmp_name='jet', proj='cyl',
                               contourLines=contourLines,
                               product_label_str=PRODUCT_LABEL,
                               vlat=lats2, vlon=lons2, u=u, v=v,
                               draw_every=draw_every, arrow_scale=arrow_scale,
                               area=regionStr, extend=extend, var_name=varName, plotStyle=plotStyle)

    plot.wait()

def extract(**args):
    area = args['area']
    variable = args['variable']
    inputLat = args['lat']
    inputLon = np.mod(args['lon'], 360.0)
    area = args['area']
    period = args['period']
    inputDate = args["date"]
    date = inputDate.strftime('%Y%m%d')
    yearStr = '%04i' % inputDate.year
    monthStr = '%02i' % inputDate.month
    yearMonthStr = yearStr + monthStr

#    if variable == 'uv':
#        variable = 'u'
#    elif variable == 'uveta':
#        variable = 'eta'

#    lat_min = regionConfig.regions[area][1]['llcrnrlat']
#    lat_max = regionConfig.regions[area][1]['urcrnrlat']
#    lon_min = regionConfig.regions[area][1]['llcrnrlon']
#    lon_max = regionConfig.regions[area][1]['urcrnrlon']

    lat_min = -999.0 
    lat_max = 999.0 
    lon_min = -999.0 
    lon_max = 999.0 
    
    # Load surface data
    if variable == 'uv':
        if period == 'monthly':    
            input_data_file = os.path.join(server_config['dataDir']['bran'],
                                           period, 'u',
                                           'u_%s_%s.nc4' % (yearStr, monthStr))
            lats, lons, zlevels, u = \
                branPlotterNew.load_BRAN_data(input_data_file, 'u',
                                                  lat_min, lat_max,
                                                  lon_min, lon_max)
            input_data_file = os.path.join(server_config['dataDir']['bran'],
                                           period, 'v',
                                           'v_%s_%s.nc4' % (yearStr, monthStr))
            lats, lons, zlevels, v = \
                branPlotterNew.load_BRAN_data(input_data_file, 'v',
                                              lat_min, lat_max,
                                              lon_min, lon_max)
        else:
            input_data_file = os.path.join(server_config['dataDir']['bran'],
                                               'averages', period, 'u',
                                               BRAN_VERSION + '_%smthavg_%s_%s.nc4' % (monthInt, months[0].strftime('%Y%m'), months[-1].strftime('%Y%m')))
            lats, lons, zlevels, u = \
                branPlotterNew.load_BRAN_data(input_data_file, 'u',
                                              lat_min, lat_max,
                                              lon_min, lon_max)
            input_data_file = os.path.join(server_config['dataDir']['bran'],
                                               'averages', period, 'v',
                                               BRAN_VERSION + '_%smthavg_%s_%s.nc4' % (monthInt, months[0].strftime('%Y%m'), months[-1].strftime('%Y%m')))
            lats, lons, zlevels, v = \
                branPlotterNew.load_BRAN_data(input_data_file, 'v',
                                              lat_min, lat_max,
                                              lon_min, lon_max)
        data = np.sqrt(u**2 + v**2)  
    else:
        if period == 'monthly':
            input_data_file = os.path.join(server_config['dataDir']['bran'],
                                          period, variable,
                                         '%s_%s_%s.nc4' % (variable,
                                                           yearStr,
                                                           monthStr))
        else:
            monthInt = int(''.join(i for i in period if i.isdigit()))
            months = dateRange.getMonths(date, monthInt)
            input_data_file = os.path.join(server_config['dataDir']['bran'],
                                          'averages', period, variable,
                                          BRAN_VERSION + '_%smthavg_%s_%s.nc4' % (monthInt, months[0].strftime('%Y%m'), months[-1].strftime('%Y%m')))

        lats, lons, zlevels, data = \
            branPlotterNew.load_BRAN_data(input_data_file, variable,
                                          lat_min, lat_max,
                                          lon_min, lon_max)

    #extract lat/lon and value
    (lat, lon), (latIndex, lonIndex) = Extractor.getGridPoint(inputLat, inputLon, lats, lons,
                                                     data)
    value = data[latIndex, lonIndex]
    if value is ma.masked:
        raise LandError()
    #return extracted values
    return (lat, lon), value

def check_basemap_exists(filename_fullpath):
    return util.check_files_exist(filename_fullpath, [COMMON_FILES[k] for k in ['mapimg', 'scale']])

def check_plot_exists(filename_fullpath):
    return os.path.exists(filename_fullpath + COMMON_FILES['img'])

def check_basemap_and_plot_exists(filename_fullpath):
    return util.check_files_exist(filename_fullpath, COMMON_FILES.values())
