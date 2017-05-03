#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#

import os.path
import numpy as np
import numpy.ma as ma

from ocean import config, util
from ocean.datasets import SST
from ocean.netcdf import SurfacePlotter
from frontPlotter import FrontPlotter
from ocean.config import regionConfig
from ocean.netcdf.extractor import Extractor, LandError
from ocean.config import regionConfig

serverCfg = config.get_server_config()

class MurPlotter(SurfacePlotter):
    DATASET = 'mur'
    PRODUCT_NAME = "MUR SST"

    VARIABLE_MAP = {
        'mursst': 'sst'
    }

    apply_to = util.Parameterise(SurfacePlotter)

    @apply_to(variable='mursst', period='daily')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'data', params['area'])
    @apply_to(variable='mursst')
    def get_ticks(self, params={}):
        return np.arange(24.0, 32.1, 0.5)

    def get_colormap_strategy(self, params={}):
        return 'nonlinear'

    # --- get_prefix ---
    def get_prefix(self, params={}):
        prefix = 'MUR_'
        return prefix

    @apply_to(variable='mursst')
    def get_suffix(self, params={}):
        suffix = '_' + params['area'] + self.FILE_EXTENSION
        return suffix

    def get_plotstyle(self, params={}):
        return 'pcolormesh'

    @apply_to(variable='mursst')
    def get_contourlines(self, params={}):
        return False

    def getPlotter(self):
        return FrontPlotter()

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
        shapefile = grid.get_filename(self.get_path(params=args), self.get_prefix(params=args), self.get_suffix(params=args), args['date'], args['period'])
        shapefile = os.path.splitext(shapefile)[0]

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
                               fill_color = fill_color,
                               extend=extend,
                               plotStyle=plotStyle,
                               contourLines=contourLines,
                               contourLabels=contourLabels,
                               smoothFactor=smoothFactor,
                               product_label_str=self.PRODUCT_NAME,
                               area=area,
                               shapefile=shapefile)
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
                                        fill_color = fill_color,
                                        regionName = area,
                                        shapefile=shapefile)

        plot.wait()

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
        

class mur(SST):
    DATASET = 'mur'
    PLOTTER = MurPlotter

    __periods__ = [
        'daily'
    ]

