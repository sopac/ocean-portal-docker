#!/usr/bin/python
#
# (c) 2013 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import datetime

import numpy as np

def stack_grids(plotter, base_year=1970, period='yearly', end_month=12):
    """
    Iterate through the dataset specified by @plotter and produce a stacked
    grid for all the years.

    Returns: lats, lons, 3D dataset(time, lats, lons)
    """

    stacked_grid = None
    this_year = datetime.date.today().year
    years = np.arange(base_year, this_year)

    for i, y in enumerate(years):
        params = {
            'variable': 'anom',
            'period': period if period != 'yearly' else '12monthly',
            'date': datetime.date(year=y, month=end_month, day=1)
        }

        grid = plotter.get_grid(params=params)

        if stacked_grid is None:
            # create the grid
            stacked_grid = np.empty(shape=[len(years)] + list(grid.data.shape))

        stacked_grid[i] = grid.data

    return (years, grid.lats, grid.lons, stacked_grid)

def calculate_spatial_trends(years, data):
    """
    Calculates the linear trend of each spatial point.

    Returns: 3D dataset([gradient, intercept], lats, lons)
    """

    nyears, nlats, nlons = data.shape
    rdata = data.reshape(nyears, nlats * nlons)

    p = np.polyfit(years, rdata, 1)

    return p.reshape(2, nlats, nlons)

class TrendGrid(object):
    """
    A wrapper class that looks like a Grid object.

    Returns: a 2D Grid-like, units = deg/decade
    """

    def __init__(self, *args, **kwargs):
        self.years, self.lats, self.lons, data = stack_grids(*args, **kwargs)
        trend = calculate_spatial_trends(self.years, data)

        # only care about the gradient, in deg C/decade
        self.data = trend[0, :, :] * 10
