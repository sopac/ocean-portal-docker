#
# (c) 2015 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea
from datetime import datetime, timedelta

from ocean.plotter import Plotter, COMMON_FILES, EXTRA_FILES, from_levels_and_colors, getCopyright, get_tick_values
from ocean.config import regionConfig
from ocean.util.pngcrush import pngcrush
from ocean.util.gdalprocess import gdal_process

try:
    from mpl_toolkits.axes_grid1 import make_axes_locatable
except ImportError:
    # support older matplotlib
    from mpl_toolkits.axes_grid import make_axes_locatable
 
SCALE_FACTOR = 0.001

class CurrentForecastPlotter(Plotter):

    def get_formatted_date(self, params={}):
        if 'step' in params:
            return datetime.strptime(params['forecast'][params['step']]['datetime'], '%d-%m-%Y %H:%M').strftime('%d %B %Y %H:%M') + " UTC"
        else:
            return ''

    def get_ticks_format(self, params={}):
        return '%.2f'

    def get_ticks(self, params={}):
        return np.array([0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 1.0, 1.5, 2.5])

    def get_labels(self, params={}):
        return self.get_ticks()

    def get_extend(self, params={}):
        return 'neither'

    def get_units(self, params={}):
        return 'm/s'

    def get_colors(self, params={}):
        return None

    def get_colormap(self, params={}):
        return 'jet'

    def get_colormap_strategy(self, params={}):
        return 'nonlinear'

    def get_plotstyle(self, params={}):
        return 'pcolormesh'

    def get_fill_color(self, params={}):
        return '1.0'

    def get_smooth_fac(self, params={}):
        return 1

    def get_contourlines(self, params={}):
        return False

    def get_contour_labels(self, params={}):
        return False

    """
        Plot mapis and color bars for WW3 forecast data. 
    """
    def plot_basemaps_and_colorbar(self, *args, **kwargs):
        #Plots the image for the map overlay.
        output_filename = kwargs.get('output_filename', 'noname.png')
        fileName, fileExtension = os.path.splitext(output_filename)
        colorbar_filename = fileName + COMMON_FILES['scale']
        outputfile_map = fileName + COMMON_FILES['mapimg']

        # Create colormap
        cm_edge_values = kwargs.get('cm_edge_values', None)
        cmp_name = kwargs.get('cmp_name', 'jet')
        extend = kwargs.get('extend', 'neither')
        cb_label_pos = kwargs.get('cb_label_pos', None)
        clabel = kwargs.get('clabel', False)
        vector = kwargs.get('vector', False)
        regionName = kwargs.get('regionName', None)
#        d_cmap = mpl.colors.ListedColormap(np.array(cmArray) / 255.0)
        d_cmap, norm = from_levels_and_colors(cm_edge_values, None, cmp_name, extend=extend)
        basemap_cmap, basemap_norm = from_levels_and_colors(cm_edge_values, None, 'binary', extend=extend)

        if cb_label_pos is None:
            tick_pos = cm_edge_values
        else:
            tick_pos = cb_label_pos

        regions = [{'lat_min':-90,
                    'lat_max':90,
                    'lon_min':110,
                    'lon_max':290,
                    'output_filename':outputfile_map}
                ]

        def _plot_basemap(region, lats, lons, data, time, 
                          units='', cb_tick_fmt="%.0f", cb_labels=None,
                          proj=self._DEFAULT_PROJ, **kwargs):

            m = Basemap(projection=proj,
                        llcrnrlat=region['lat_min'],
                        llcrnrlon=region['lon_min'],
                        urcrnrlat=region['lat_max'],
                        urcrnrlon=region['lon_max'],
                        resolution='i')

            # Plot data
            m.drawmapboundary(linewidth=1.0, fill_color='0.02')
            x2, y2 = m(*np.meshgrid(lons, lats))

            u = data[0][time]
            v = data[1][time]
            mag = np.sqrt(u**2 + v**2)

            #img = m.pcolormesh(x2, y2, mag, shading='flat', cmap=d_cmap, norm=norm)
            img = m.pcolormesh(x2, y2, mag, shading='flat', cmap=basemap_cmap, norm=basemap_norm)
            img.set_clim(cm_edge_values.min(), cm_edge_values.max())

            plt.savefig(region['output_filename'], dpi=120,
                        bbox_inches='tight', pad_inches=0.0)
            # generate shape file
            gdal_process(region['output_filename'], region['lon_min'],
                                                    region['lat_max'],
                                                    region['lon_max'],
                                                    region['lat_min'])

            pngcrush(region['output_filename'])


            #plot contouring labels
            if clabel:
                labels = plt.clabel(img, cm_edge_values[::4], inline=True, fmt='%.0f', colors='k', fontsize=5, zorder=2)
                bbox_props = dict(boxstyle="round", fc="w", ec="w", alpha=0.9)
                for text in labels:
                    text.set_linespacing(1)
                    text.set_bbox(bbox_props)
 
            #plot vectors
            baseName = os.path.splitext(region['output_filename'])[0]
            plt.clf()
            m.drawmapboundary(linewidth=0.0)
            
            if regionName == 'pac':
                every = 50 
                scale = 10
            else: 
                every = 10 
                scale = 10
            lons = lons[::every]
            lats = lats[::every]
            x2, y2 = m(*np.meshgrid(lons, lats))
            u2 = u[::every, ::every]
            v2 = v[::every, ::every]
#            u2 = u[::every, ::every]
#            v2 = v[::every, ::every]
            rad = np.arctan2(v2, u2)
            m.quiver(x2, y2, np.cos(rad), np.sin(rad), scale=scale, zorder=3, scale_units='inches', pivot='middle')

            arrowFile = baseName + '_arrow.png'
            plt.savefig(arrowFile, dpi=120,
                        bbox_inches='tight', pad_inches=0.0, transparent=True)
            # generate shape file
            gdal_process(arrowFile, region['lon_min'],
                                    region['lat_max'],
                                    region['lon_max'],
                                    region['lat_min'])

            pngcrush(arrowFile)
#            m.drawmapboundary(linewidth=0.0)

#            m.drawcoastlines(linewidth=0.5, color='#505050', zorder=8)
#            m.fillcontinents(color='#F1EBB7', zorder=7)
#            m.fillcontinents(color='0.58', zorder=7)

            # Save figure
#            plt.savefig(region['output_filename'], dpi=120,
#                        bbox_inches='tight', pad_inches=0.0)
            plt.close()
#            pngcrush(region['output_filename'])

        def _plot_colorbar(lats, lons, data, time,
                           units='', cb_tick_fmt="%.0f",
                           cb_labels=None, extend='both',
                           proj=self._DEFAULT_PROJ, **kwargs):
            # Draw colorbar
            fig = plt.figure(figsize=(1.5,2))
            ax1 = fig.add_axes([0.05, 0.02, 0.125, 0.96])

            cb = mpl.colorbar.ColorbarBase(
                    ax1,
                    cmap=d_cmap,
                    norm=norm,
                    orientation='vertical',
                    drawedges='True',
                    extend=extend,
                    ticks=tick_pos)

            if cb_labels is None:
                cb.set_ticklabels([cb_tick_fmt % k for k in cm_edge_values])
            else:
                cb.set_ticklabels(cb_labels)
            cb.set_label(units,
                    rotation='horizontal',
                    fontsize=6,
                    fontweight='bold')

            for tick in cb.ax.get_yticklabels():
                tick.set_fontsize(6)
                tick.set_fontweight('bold')

            plt.savefig(colorbar_filename,
                    dpi=120,
                    transparent=True)
            plt.close()
            pngcrush(colorbar_filename)

        if regionName is not None and regionName is not 'pac':
            regions = [convertRegionBounds(regionConfig.regions[regionName], outputfile_map)]

        for region in regions:
            self.queue_plot(_plot_basemap, region, *args, **kwargs)

        self.queue_plot(_plot_colorbar, *args, **kwargs)

    def plot_surface_data(self, *args, **kwargs):
        def _plot_surface_data(lats, lons, data, time,
                               lat_min, lat_max, lon_min, lon_max,
                               output_filename='noname.png', title='', units='',
                               cm_edge_values=None, cb_tick_fmt="%.0f",
                               cb_labels=None, cb_label_pos=None,
                               colormap_strategy='nonlinear',
                               cmp_name='jet', colors=None, extend='both',
                               fill_color='1.0',
                               plotStyle='contourf', contourLines=True,
                               contourLabels=True, smoothFactor=1,
                               proj=self._DEFAULT_PROJ, product_label_str=None,
                               vlat=None, vlon=None, u=None, v=None,
                               draw_every=1, arrow_scale=10,
                               resolution=None, area=None, boundaryInUse='True'):

            d_cmap, norm = from_levels_and_colors(cm_edge_values, None, cmp_name, extend=extend)

            m = Basemap(projection=proj,
                        llcrnrlat=lat_min, llcrnrlon=lon_min,
                        urcrnrlat=lat_max, urcrnrlon=lon_max,
                        resolution='i')

            # Plot data
            x2, y2 = m(*np.meshgrid(lons, lats))

            u = data[0][time]
            v = data[1][time]
            mag = np.sqrt(u**2 + v**2)

            img = m.pcolormesh(x2, y2, mag, shading='flat', cmap=d_cmap, norm=norm)
            img.set_clim(cm_edge_values.min(), cm_edge_values.max())

            #plot vectors
            if area == 'pac':
                every = 50
                scale = 10
            else:
                every = 10
                scale = 10

            lons = lons[::every]
            lats = lats[::every]
            x2, y2 = m(*np.meshgrid(lons, lats))
            u2 = u[::every, ::every]
            v2 = v[::every, ::every]
            rad = np.arctan2(v2, u2)
            m.quiver(x2, y2, np.cos(rad), np.sin(rad), scale=scale, zorder=3, scale_units='inches', pivot='middle')

            # Draw land, coastlines, parallels, meridians and add title
            m.drawmapboundary(linewidth=1.0, fill_color=fill_color)
            m.drawcoastlines(linewidth=0.5, color='#505050', zorder=8)
            m.fillcontinents(color='0.58', zorder=7)

            parallels, p_dec_places = get_tick_values(lat_min, lat_max)
            meridians, m_dec_places = get_tick_values(lon_min, lon_max)
            m.drawparallels(parallels, labels=[True, False, False, False],
                            fmt='%.' + str(p_dec_places) + 'f',
                            fontsize=6, dashes=[3, 3], color='gray')
            m.drawmeridians(meridians, labels=[False, False, False, True],
                            fmt='%.' + str(m_dec_places) + 'f',
                            fontsize=6, dashes=[3, 3], color='gray')

            plt.title(title, fontsize=9)

            # Draw colorbar
            ax = plt.gca()
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size=0.2, pad=0.3)
            if cb_label_pos is None:
                tick_pos = cm_edge_values
            else:
                tick_pos = cb_label_pos

            if boundaryInUse == 'True':
                cb = plt.colorbar(img, cax=cax,
    #                             spacing='proportional',
                                 spacing='uniform',
                                 drawedges='False',
                                 orientation='vertical',
                                 extend=extend,
                                 ticks=tick_pos,
                                 boundaries=cm_edge_values)
            else:
                cb = plt.colorbar(img, cax=cax,
                                 spacing='uniform',
                                 drawedges='False',
                                 orientation='vertical',
                                 extend=extend,
                                 ticks=tick_pos)

            if cb_labels is None:
                cb.set_ticklabels([cb_tick_fmt % k for k in cm_edge_values])
            else:
                cb.set_ticklabels(cb_labels)
            for tick in cb.ax.get_yticklabels():
                tick.set_fontsize(7)
            cb.set_label(units, fontsize=8)

            # Patch for graphics bug that affects label positions for
            # long/narrow plots
            lat_extent = np.float(lat_max) - np.float(lat_min)
            lon_extent = np.float(lon_max) - np.float(lon_min)
            aspect_ratio = abs(lon_extent / lat_extent)

            if aspect_ratio > 1.7:
                copyright_label_yadj = -0.25
            else:
                copyright_label_yadj = -0.10
            if aspect_ratio < 0.7:
                copyright_label_xadj = -0.2
                product_label_xadj = 1.4
            else:
                copyright_label_xadj = -0.1
                product_label_xadj = 1.04

            # Draw copyright and product labels
            box = TextArea(getCopyright(),
                           textprops=dict(color='k', fontsize=6))
            copyrightBox = AnchoredOffsetbox(loc=3, child=box,
                                             borderpad=0.1,
                                             bbox_to_anchor=(copyright_label_xadj, copyright_label_yadj),
                                             frameon=False,
                                             bbox_transform=ax.transAxes)
            ax.add_artist(copyrightBox)

            if product_label_str is not None:
                box = TextArea(product_label_str,
                               textprops=dict(color='k', fontsize=6))
                copyrightBox = AnchoredOffsetbox(loc=4, child=box,
                                                 borderpad=0.1,
                                                 bbox_to_anchor=(product_label_xadj, copyright_label_yadj),
                                                 frameon=False,
                                                 bbox_transform=ax.transAxes)
                ax.add_artist(copyrightBox)

            # Save figure
            plt.savefig(output_filename, dpi=150,
                        bbox_inches='tight', pad_inches=0.6)

            plt.close()

            pngcrush(output_filename)

        self.queue_plot(_plot_surface_data, *args, **kwargs)

def convertRegionBounds(regionBound, outputfile):

    bounds = {'lat_min':regionBound[1]['llcrnrlat'],
     'lat_max':regionBound[1]['urcrnrlat'],
     'lon_min':regionBound[1]['llcrnrlon'],
     'lon_max':regionBound[1]['urcrnrlon'],
     'output_filename':outputfile}    
    return bounds
