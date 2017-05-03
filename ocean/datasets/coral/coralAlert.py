#
# (c) 2015 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

from mpl_toolkits.basemap import Basemap, shiftgrid
from matplotlib.path import Path
import numpy as np
import bisect
from netCDF4 import Dataset

from ocean import util, config

country = {
    'cook': 'COOKS',
    'cook_nor': 'COOKS_NORTH',
    'cook_sou': 'COOKS_SOUTH',
    'fsm': 'FSM',
    'fsm_east': 'FSM_EAST',
    'fsm_west': 'FSM_WEST',
    'fiji': 'FIJI',
    'kiribati': 'KIRIBATI',
    'kiribati_gilbert': 'KIRIBATI_GILBERT',
    'kiribati_phoenix': 'KIRIBATI_PHOENIX',
    'kiribati_nor_line': 'KIRIBATI_LINE_NORTH',
    'kiribati_sou_line': 'KIRIBATI_LINE_SOUTH',
    'marshall': 'MARSHALL',
    'nauru': 'NAURU',
    'niue': 'NIUE',
    'palau': 'PALAU',
    'png': 'PNG',
    'samoa': 'SAMOA',
    'wsm_nor': 'SAMOA',
    'wsm_sou': 'SAMOA',
    'solomon': 'SOLOMON',
    'tonga': 'TONGA',
    'tuvalu': 'TUVALU',
    'vanuatu': 'VANUATU',
    'vanuatu_northern': 'VANUATU',
    'vanuatu_central': 'VANUATU',
    'vanuatu_southern': 'VANUATU'
}


def filter_alert(params, grid):

    #read shapefile
    #For cylindrical equidistant projection (cyl), this does nothing (i.e. x,y == lon,lat).
    #Therefore the converting from Geographic (lon/lat) to Map Projection (x/y) Coordinates is not necessary here.
    map = Basemap(llcrnrlon=110,llcrnrlat=-90,urcrnrlon=290,urcrnrlat=90,
        resolution='c', projection='cyl')

    if params['variable'] == 'outlook':
        crw = map.readshapefile(util.get_resource('maps', 'layers', 'CRW_Outlook_EEZ'),
                                'crw')
    elif params['variable'] == 'daily':
        crw = map.readshapefile(util.get_resource('maps', 'layers', 'CRW_Outlines'),
                                'crw')

    collection = []
    max = None

#    shape_area = country[params['area']]
    shape_area = country[params['area'].lower()]
    for info, shape in zip(map.crw_info, map.crw):
        if info['ID'] == shape_area or info['SUBREGION'] == shape_area:
            collection.append(np.array(shape))

    for polygon in collection:
        path = Path(polygon)
        poly_lons = polygon.T[0]
        poly_lats = polygon.T[1]

        lon_min = np.min(poly_lons)
        lon_max = np.max(poly_lons)
        lat_min = np.min(poly_lats)
        lat_max = np.max(poly_lats)

        lons, lats, data = grid.lons, grid.lats, grid.data
        if lats[0] > lats[-1]:
            flippedlats = np.flipud(lats)
            start_lat = bisect.bisect_left(flippedlats, lat_min)
            end_lat = bisect.bisect_right(flippedlats, lat_max)
            start_latr = start_lat
            end_latr = end_lat
            start_lat = lats.size - end_latr
            end_lat = lats.size - start_latr
        else:
            start_lat = bisect.bisect_left(lats, lat_min)
            end_lat = bisect.bisect_right(lats, lat_max)
            
        start_lon = bisect.bisect_left(lons, lon_min)
        end_lon = bisect.bisect_right(lons, lon_max)

        lat_clip = lats[start_lat: end_lat]
        lon_clip = lons[start_lon: end_lon]

        x, y = np.meshgrid(lon_clip, lat_clip)
        shape_2d = x.shape

        x_flat = x.flatten()
        y_flat = y.flatten()
        points = zip(x_flat, y_flat)

        mask = [path.contains_point(point) for point in points]
        mask_array = np.array(mask)
        mask_array = mask_array.reshape(shape_2d)
        mask_array_logical_not = np.logical_not(mask_array)

        data_clip = data[start_lat:end_lat, start_lon:end_lon]
        new_mask = np.ma.mask_or(data_clip.mask, mask_array_logical_not)

        data_clip.mask = new_mask
        local_max = np.max(data_clip)
        if local_max > max:
            max = local_max

    return max
