#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import bisect
import os.path

import numpy as np

from ocean import util, config
from ocean.config import regionConfig
from ocean.netcdf import Gridset
from ocean.plotter import Plotter
from ocean.processing.trends import TrendGrid

serverCfg = config.get_server_config()

class SurfacePlotter(object):
    """
    Plot surface data from a netCDF grid.

    Override class hooks to specify the location for data.

    Use the decorator @SurfacePlotter.apply_to to tag methods to bind to
    specific parameters. Most tightly binding function wins.
    """

    BASE_YEAR = '1950'
    FILE_EXTENSION = '.nc'

    apply_to = util.Parameterise()

    # --- get_path ---
    @apply_to()
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'averages', params['period'])

    @apply_to(variable='dec')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'decile', self.BASE_YEAR, params['period'])

    def get_prefix(self, params={}):
        return ''

    # --- get_suffix ---
    @apply_to(variable='dec')
    def get_suffix(self, params={}):
        return '_dec' + self.FILE_EXTENSION

    @apply_to()
    def get_suffix(self, params={}):
        return self.FILE_EXTENSION

    @apply_to(variable='dec')
    def get_suffix_prelim(self, params={}):
        return '_preliminary_dec' + self.FILE_EXTENSION

    @apply_to()
    def get_suffix_prelim(self, params={}):
        return '_preliminary' + self.FILE_EXTENSION

    def get_formatted_date(self, params={}):
        formatted_date = ''
        if params['variable'] == 'trend':
            if params['period'] == 'monthly':
                formatted_date = "%s, %s to present" % (params['date'].strftime('%B'),
                                      params['baseYear'])
            if params['period'] == '3monthly':
                formatted_date = self._get_formatted_date_trend(params, 3)
            if params['period'] == '6monthly':
                formatted_date = self._get_formatted_date_trend(params, 6)
            if params['period'] == 'yearly':
                formatted_date = '%s to present' % (params['baseYear'])
        else:
            if params['period'] == 'daily':
                formatted_date = params['date'].strftime('%d %B %Y')
            if params['period'] == 'weekly':
                weekdays = util.getWeekDays(params['date'])
                formatted_date = weekdays[0].strftime('%d %B %Y') + ' to ' + weekdays[-1].strftime('%d %B %Y')                 
            if params['period'] == '4weeks':
                formatted_date = params['date'].strftime('%d %B %Y')
            elif params['period'] == '8weeks':
                formatted_date = params['date'].strftime('%d %B %Y')
            elif params['period'] == '12weeks':
                formatted_date = params['date'].strftime('%d %B %Y')
            if params['period'] == 'monthly':
                formatted_date = params['date'].strftime('%B %Y')
            if params['period'] == '3monthly':
                formatted_date = self._get_formatted_date(params, 3)
            if params['period'] == '6monthly':
                formatted_date = self._get_formatted_date(params, 6)
            if params['period'] == '12monthly':
                formatted_date = self._get_formatted_date(params, 12)
            if params['period'] == 'yearly':
                formatted_date = params['date'].strftime('%Y')
        return formatted_date 

    # --- get_formatted_date ---
    def _get_formatted_date(self, params, range):
        months = util.getMonths(params['date'], range)
        return "%s to %s" % (months[0].strftime('%B %Y'),
                             months[-1].strftime('%B %Y'))

    def _get_formatted_date_trend(self, params, range):
        months = util.getMonths(params['date'], range)
        return "%s to %s, %s to present" % (months[0].strftime('%B'),
                                            months[-1].strftime('%B'),
                                            params['baseYear'])


    # --- get_ticks_format ---
    @apply_to()
    def get_ticks_format(self, params={}):
        return '%.1f'
    #GAS remove this code so all colorbars have one decimal place
    @apply_to(variable='mean')
    def get_ticks_format(self, params={}):
        return '%.0f'

    # --- get_labels ---
    @apply_to()
    def get_labels(self, params={}):
        return (None, None)

    @apply_to(variable='dec')
    def get_labels(self, params={}):
        return (['Lowest on \nrecord',
                 'Very much \nbelow average \n[1]',
                 'Below average \n[2-3]',
                 'Average \n[4-7]',
                 'Above average \n[8-9]',
                 'Very much \nabove average \n[10]',
                 'Highest on \nrecord'],
                [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])

    # --- get_ticks ---GAS change if statement to detect pac instead of PI
    @apply_to(variable='mean')
    def get_ticks(self, params={}):
        try:
            if regionConfig.regions[params['area']][0] == 'pac':
                return np.arange(20.0, 32.1, 1.0)
            else:
                pass
        except KeyError:
            pass
        return np.arange(0.0, 32.1, 2.0)

    @apply_to(variable='anom')
    def get_ticks(self, params={}):
        return np.arange(-2.0, 2.01, 0.5)

    @apply_to(variable='dec')
    def get_ticks(self, params={}):
        # range is chosen to match label positions
        return np.arange(0.5, 7.51, 1)

    @apply_to(variable='trend')
    def get_ticks(self, params={}):
        return np.arange(-0.6, 0.61, 0.1)

    @apply_to(variable='alt')
    def get_ticks(self, params={}):
        return np.arange(-300, 300, 50)

    @apply_to(variable='rec')
    def get_ticks(self, params={}):
        return np.arange(-300, 300, 50)

    # --- get_extend ---
    @apply_to()
    def get_extend(self, params={}):
        extend = 'both'
        if params['variable'] == 'dec':
            extend = 'neither'
        else:
            extend = 'both'
        return extend

#    @apply_to(variable='dec')
#    def get_extend(self, params={}):
#        return 'neither'

    # --- get_contour_labels ---
    @apply_to()
    def get_contour_labels(self, params={}):
        return True

    @apply_to(variable='sla')
    def get_contour_labels(self, params={}):
        return False

    #GAS Remove Contour labels
    @apply_to(variable='anom')
    def get_contour_labels(self, params={}):
        return False

    @apply_to(variable='dec')
    def get_contour_labels(self, params={}):
        return False

    # --- get_title ---
#    @apply_to()
    def get_title(self, params={}):
        d = {
            'mean': "Average Sea Surface Temperature",
            'anom': "Average Sea Surface Temperature Anomaly",
            'dec': "Average Sea Surface Temperature Deciles",
            'trend': "Trend",
            'alt': "Sea Level Altimetry",
            'rec': "Sea Level Reconstruction",
            'sla': "Near Real Time Sea Level Anomaly",
            'height': "Sea Level Forecast",
            'ssta': "Sea Surface Temperature Forecast",
            'mursst': "MUR Sea Surface Temperature",
            'sst': "Sea Surface Temperature Forecast"
        }

        return d[params['variable']]

    # --- get_period_name ---
    @apply_to()
    def get_period_name(self, params={}):
        d = {
            'daily': "Daily",
            'weekly': "Weekly",
            '4weeks': "4 Weeks",
            '8weeks': "8 Weeks",
            '12weeks': "12 Weeks",
            'monthly': "Monthly",
            '3monthly': "3 monthly",
            'seasonal': "Seasonal",
            '6monthly': "6 monthly",
            '12monthly': "12 monthly",
            'yearly': "Yearly",
        }

        return d[params['period']]

    # --- get_units ---
    @apply_to()
    def get_units(self, params={}):
        return ur'\u00b0' + 'C' # degrees C

    @apply_to(variable='dec')
    def get_units(self, params={}):
        return ''

    @apply_to(variable='trend')
    def get_units(self, params={}):
        return ur'\u00b0' + 'C/decade' # degrees C/decade

    # --- get_colormap_strategy---
    def get_colormap_strategy(self, params={}):
        return 'discrete'

#    @apply_to()
    def get_colormap(self, params={}):
        cm_name = 'RdBu_r'
        if params.get('variable') == 'mean':
            cm_name = 'jet'
#            cm_name = 'binary'
        return cm_name

#    @apply_to(variable='mean')
#    def get_colormap(self, params={}):
#        return 'jet'

    # --- get_colors ---
    @apply_to()
    def get_colors(self, params={}):
        return None

    @apply_to()
    def get_basemap_colors(self, params={}):
        return None 

    def get_fill_color(self, params={}):
        #return '1.0'
        return '0.02'

    #GAS ---- get_plotstyle ---
    def get_plotstyle(self, params={}):
        style = 'pcolormesh'
        if params['variable'] == 'anom':
            style = 'contourf'
        else:
            style = 'contourf'
        return style

#    @apply_to(variable='anom')
#    def get_plotstyle(self, params={}):
#        return 'contourf'

    #GAS ---- get_contourlines ---
    @apply_to()
    def get_contourlines(self, params={}):
        return True

    @apply_to(variable='mean')
    def get_contourlines(self, params={}):
        return True

    #GAS ---- get_smooth_fac ---
    @apply_to(variable='anom')
    def get_smooth_fac(self, params={}):
        try:
            if regionConfig.regions[params['area']][0] == 'pac':
                return 1
            else:
                pass
        except KeyError:
            pass
        return 20

    @apply_to(variable='dec')
    def get_smooth_fac(self, params={}):
        try:
            if regionConfig.regions[params['area']][0] == 'pac':
                return 1
            else:
                pass
        except KeyError:
            pass
        return 20

    @apply_to()
    def get_smooth_fac(self, params={}):
        return 1

    # --- get_grid ---
    @apply_to()
    def get_grid(self, params={}, **kwargs):
        """
        Request a Grid object for this dataset.

        Override this method to access grids in a different way.
        """

        gridvar = self.get_variable_mapping(params=params)

        return Gridset(self.get_path(params=params), gridvar, params['period'],
                       prefix=self.get_prefix(params=params),
                       suffix=self.get_suffix(params=params),
                       suffix2=self.get_suffix_prelim(params=params),
                       date=params['date'],
                       **kwargs)

    @apply_to(variable='trend')
    def get_grid(self, params={}, **kwargs):
        """
        Request a spatial trend map.
        """

        return TrendGrid(self,
                         base_year=params['baseYear'],
                         period=params['period'],
                         end_month=params['date'].month)

    # ---
    def get_variable_mapping(self, params={}):
        var = params['variable']

        try:
            return self.VARIABLE_MAP[var]
        except KeyError:
            return var

    def getPlotter(self):
        return Plotter()

    def plot(self, outputFilename, **args):
        """
        Plot the thumbnail image and also the east and west map images.
        """

        area = args['area']
        variable = args['variable']

        args['formattedDate'] = self.get_formatted_date(params=args)
        output_filename = serverCfg['outputDir'] + outputFilename + '.png'

        regionLongName = regionConfig.regions[area][2]
        title = regionLongName + '\n'

        if 'period' in args:
            title += "%s %s: %s" % (self.get_period_name(params=args),
                                    self.get_title(params=args),
                                    args['formattedDate'])

        units = self.get_units(params=args)
        cmap_name = self.get_colormap(params=args)
        cb_ticks = self.get_ticks(params=args)
        cb_tick_fmt = self.get_ticks_format(params=args)
        cb_labels, cb_label_pos = self.get_labels(params=args)
        extend = self.get_extend(params=args)
        contourLabels = self.get_contour_labels(params=args)
        plotStyle = self.get_plotstyle(params=args)#GAS
        contourLines = self.get_contourlines(params=args)#GAS
        smoothFactor = self.get_smooth_fac(params=args)#GAS
        colors = self.get_colors(params=args)
        basemap_colors = self.get_basemap_colors(params=args)
        fill_color = self.get_fill_color(params=args)
        colormap_strategy = self.get_colormap_strategy(params=args)
        

        plot = self.getPlotter()

        lat_min = regionConfig.regions[area][1]['llcrnrlat']
        lat_max = regionConfig.regions[area][1]['urcrnrlat']
        lon_min = regionConfig.regions[area][1]['llcrnrlon']
        lon_max = regionConfig.regions[area][1]['urcrnrlon']

        grid = self.get_grid(params=args,
                             lonrange=(lon_min, lon_max),
                             latrange=(lat_min, lat_max))

        plot.plot_surface_data(grid.lats, grid.lons, grid.data,
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
                          #     fill_color = fill_color,
                               extend=extend,
                               plotStyle=plotStyle,
                               contourLines=contourLines,
                               contourLabels=contourLabels,
                               smoothFactor=smoothFactor,
                               product_label_str=self.PRODUCT_NAME,
                               area=area)
        grid = self.get_grid(params=args)

        if variable == 'dec':
            # Mask out polar region to avoid problem of calculating deciles
            # over sea ice
            grid.data.mask[0:bisect.bisect_left(grid.lats,-60),:] = True
            grid.data.mask[bisect.bisect_left(grid.lats,60):-1,:] = True

        plot.plot_basemaps_and_colorbar(grid.lats, grid.lons, grid.data,
                                        output_filename=output_filename,
                                        units=units,
                                        cm_edge_values=cb_ticks,
                                        cb_tick_fmt=cb_tick_fmt,
                                        cb_labels=cb_labels,
                                        cb_label_pos=cb_label_pos,
                                        cmp_name=cmap_name, extend=extend,
                                        colormap_strategy = colormap_strategy,
                                        colors = colors,
                                        basemap_colors = basemap_colors,
                                        fill_color = fill_color)

        plot.wait()
