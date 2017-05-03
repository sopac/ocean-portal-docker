#
# (c) 2015 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

import os
import shutil
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea
from matplotlib.transforms import offset_copy
from mpl_toolkits.basemap import Basemap
try:
    from mpl_toolkits.axes_grid1 import make_axes_locatable
except ImportError:
    # support older matplotlib
    from mpl_toolkits.axes_grid import make_axes_locatable

from ocean.plotter import Plotter, COMMON_FILES, from_levels_and_colors, guess_resolution, getCopyright, get_grid_edges, get_tick_values
#from ocean.plotter import * 
from ocean.config import regionConfig
from ocean.config.regionConfig import regions
from ocean.util.pngcrush import pngcrush
from ocean.util.gdalprocess import gdal_process
 
class FrontPlotter(Plotter):

    def plot_surface_data(self, *args, **kwargs):

        def _plot_surface_data(lats, lons, data,
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
                               resolution=None, area=None, boundaryInUse='True', shapefile=None):

            '''
            TODO
            color map needs to be consilidated into one method. The existing discrete_colormap method is
            less flexible. Actually, the overall plot method needs to be more flexible.
            1. Introduce the colormap strategy
                discrete: discrete_cmap
                levels: from_levels_and_colors
            2. Depending on the strategy, various combination of the arguments should be passed in.
                discrete: cmp_name
                          extend
                          cm_edge_values
                levels: color_array
                        extend
                        cm_edge_values
            '''

            if resolution is None and area is not None:
                # try and get a resolution from the area default
                resolution = regions[area][3].get('resolution', None)

            if resolution is None:
                # still no resolution? try and guess
                resolution = guess_resolution(lat_min, lat_max,
                                              lon_min, lon_max)
            m = Basemap(projection=proj,
                        llcrnrlat=lat_min, llcrnrlon=lon_min,
                        urcrnrlat=lat_max, urcrnrlon=lon_max,
                        resolution=resolution)

            #GAS this was removed because different colour ranges makes comparison difficult
            #if cm_edge_values is None:
            #    cm_edge_values = get_tick_values(data.min(), data.max(), 10)[0]
            n_colours = cm_edge_values.size - 1
            if colormap_strategy == 'discrete':
                d_cmap = discrete_cmap(cmp_name, n_colours, extend=extend)
                norm = None
            elif colormap_strategy == 'levels':
                d_cmap, norm = from_levels_and_colors(cm_edge_values, np.array(colors) / 255.0, None, extend=extend)
            elif colormap_strategy == 'nonlinear':
                d_cmap, norm = from_levels_and_colors(cm_edge_values, None, cmp_name, extend=extend)

            #GAS Smoothing section based on smoothFactor
            if smoothFactor > 1:
            #if smoothFactor > 1 and (lat_extent>20 or lon_extent>20):
                size=int(smoothFactor)
                x,y = np.mgrid[-size:size+1,-size:size+1]
                g = np.exp(-(x**2/float(size)+y**2/float(size)))
                g=g/g.sum()
                #data=np.ma.masked_less(data,-998)a
                data[data<-9.9]=0
                data[data>1000]=5
                data=convolve2d(data, g, mode='same', boundary='symm')
                #a=ma.masked_less(data,-998)
            #np.savetxt('/data/comp/raster/filename.txt',data,delimiter=",")a

            # Plot data
            x, y = None, None
            if plotStyle == 'contourf':
                x, y = m(*np.meshgrid(lons, lats))
                img = plt.contourf(x, y, data, levels=cm_edge_values, norm=norm,
                                  shading='flat', cmap=d_cmap, extend=extend)
            elif plotStyle == 'pcolormesh':
                # Convert centre lat/lons to corner values required for
                # pcolormesh
                lons2 = get_grid_edges(lons)
                lats2 = get_grid_edges(lats)
                x2, y2 = m(*np.meshgrid(lons2, lats2))
                img = m.pcolormesh(x2, y2, data, shading='flat', cmap=d_cmap, norm=norm)
            # Draw contours
            if contourLines:
                if x is None:
                    x, y = m(*np.meshgrid(lons, lats))
                #GAS negative contour not to be dashed
                plt.rcParams['contour.negative_linestyle'] = 'solid'
                cnt = plt.contour(x, y, data, levels=cm_edge_values, norm=norm,
                                 colors = 'k', linewidths = 0.4, hold='on')
                if contourLabels:
                    plt.clabel(cnt, inline=True, fmt=cb_tick_fmt, fontsize=8)

            img.set_clim(cm_edge_values.min(), cm_edge_values.max())
            # Plot vector data if provided

            if (u is not None) and (v is not None) and \
               (vlat is not None) and (vlon is not None):
                # Draw vectors
                if draw_every is not None:
                    draw_vector_plot(m, vlon, vlat, u, v,
                                     draw_every=draw_every,
                                     arrow_scale=arrow_scale)
            
            if shapefile is not None:
                if os.path.exists(shapefile + ".shp"):
                    front_info = m.readshapefile(shapefile, 'front')
		marker = '_'
		if hasattr(m, 'front'):
		    for front in m.front:
		    	m.plot(front[0] if front[0] > 0 else front[0] +360, front[1], color='k', marker=marker, markersize=1, markeredgewidth=1)

            # Draw land, coastlines, parallels, meridians and add title
            m.drawmapboundary(linewidth=1.0, fill_color=fill_color)
            m.drawcoastlines(linewidth=0.5, color='#505050', zorder=8)
#            m.fillcontinents(color='#F1EBB7', zorder=7)
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
                                 spacing='uniform',
                                 drawedges='False',
                                 norm=norm,
                                 orientation='vertical',
                                 extend=extend,
                                 ticks=tick_pos)
                                 #boundaries=cm_edge_values)
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
                copyright_label_yadj = -0.15
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
                        bbox_inches='tight',
                        pad_inches=0.6)
            plt.close()

            pngcrush(output_filename)

        self.queue_plot(_plot_surface_data, *args, **kwargs)


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
        olors = kwargs.get('colors', None)
        fill_color = kwargs.get('fill_color', '0.0')
        regionName = kwargs.get('regionName', None)
        shapefile = kwargs.get('shapefile', None)

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

        def _plot_basemap(region, lats, lons, data, 
                          units='', cb_tick_fmt="%.0f", cb_labels=None,
                          proj=self._DEFAULT_PROJ, **kwargs):
           
            m = Basemap(projection=proj,
                        llcrnrlat=region['lat_min'],
                        llcrnrlon=region['lon_min'],
                        urcrnrlat=region['lat_max'],
                        urcrnrlon=region['lon_max'],
                        resolution='c')
            m.drawmapboundary(linewidth=0.0, fill_color='0.02')
            # Convert centre lat/lons to corner values required for pcolormesh
            lons2 = get_grid_edges(lons)
            lats2 = get_grid_edges(lats)

            # Plot data
            x2, y2 = m(*np.meshgrid(lons2, lats2))
            #img = m.pcolormesh(x2, y2, data, shading='flat', cmap=d_cmap, norm=norm)
            img = m.pcolormesh(x2, y2, data, shading='flat', cmap=basemap_cmap, norm=basemap_norm)
            img.set_clim(cm_edge_values.min(), cm_edge_values.max())

            plt.savefig(region['output_filename'], dpi=120,
                        bbox_inches='tight', pad_inches=0.0)
            # generate shape file
            gdal_process(region['output_filename'], region['lon_min'],
                                                    region['lat_max'],
                                                    region['lon_max'],
                                                    region['lat_min'])

            pngcrush(region['output_filename'])

            #plot front
            baseName = os.path.splitext(region['output_filename'])[0]
#            plt.clf()
            m.drawmapboundary(linewidth=0.0)
            if shapefile is not None:
                if os.path.exists(shapefile + ".shp"):
                    shutil.copyfile(shapefile + '.shp', baseName + '_front.shp')
                    shutil.copyfile(shapefile + '.shx', baseName + '_front.shx')
                    shutil.copyfile(shapefile + '.dbf', baseName + '_front.dbf')

                    front_info = m.readshapefile(shapefile, 'front')
		marker = '_'
		if hasattr(m, 'front'):
		    for front in m.front:
		    	m.plot(front[0] if front[0] > 0 else front[0] +360, front[1], color='k', marker=marker, markersize=1, antialiased=False)
                frontFile = baseName + '_front.png'
                plt.savefig(frontFile, dpi=120,
                            bbox_inches='tight', pad_inches=0.0, transparent=True)
                # generate shape file
#                gdal_process(frontFile, region['lon_min'],
#                                        region['lat_max'],
#                                        region['lon_max'],
#                                        region['lat_min'])
#
                pngcrush(frontFile)
            
    

           # m.drawmapboundary(linewidth=0.0, fill_color=fill_color)
           # m.fillcontinents(color='#F1EBB7', zorder=7)

            # Save figure
           # plt.savefig(region['output_filename'], dpi=150,
           #             bbox_inches='tight', pad_inches=0.0)
            plt.close()

           # pngcrush(region['output_filename'])

        def _plot_colorbar(lats, lons, data,
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

def convertRegionBounds(regionBound, outputfile):

    bounds = {'lat_min':regionBound[1]['llcrnrlat'],
     'lat_max':regionBound[1]['urcrnrlat'],
     'lon_min':regionBound[1]['llcrnrlon'],
     'lon_max':regionBound[1]['urcrnrlon'],
     'output_filename':outputfile}    
    return bounds
