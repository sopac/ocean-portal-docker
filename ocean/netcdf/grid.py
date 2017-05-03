#
# (c) 2013 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Nick Summons <n.summons@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import os.path
import bisect
import datetime
import numpy as np
from netCDF4 import Dataset
from mpl_toolkits.basemap import shiftgrid 

from ocean import util
from ocean.config import get_server_config
from ocean.util.dateRange import getMonths
from ocean.core import ReportableException

config = get_server_config()

class FileNotFound(ReportableException):
    def __init__(self, filename, msg="Data not available"):
        if config['debug']:
            msg += ': ' + filename

        ReportableException.__init__(self, msg)

class GridWrongFormat(ReportableException):
    pass

def get_subset_idxs(x, x_min, x_max):

    if x_min == x_max:
        closest_idx = np.abs(np.array(x) - x_min).argmin()
        return closest_idx, closest_idx + 1

    # assuming that x is sorted, find indexes to the left of x_min and the
    # right of x_max, because of weirdly sized bins, extend the bins by
    # 1 degree each way
    start_idx = bisect.bisect_left(x, x_min - 1.0)
    end_idx = bisect.bisect_right(x, x_max + 1.0)

    return start_idx, end_idx

class Grid(object):
    """
    Generic accessor for NetCDF grids. Able to handle data referenced in
    multiple dimensions given the specified subset.

    Subclass this class to handle specific grid layouts.
    """

    # a list of possible variables for latitudes
    LATS_VARIABLE = ['lat']

    # a list of possible variables for longitude
    LONS_VARIABLE = ['lon']

    #time variable name
    TIME_VARIABLE = []
    GRID_SPACING = 1

    #def __init__(self, filename, variable,
    def __init__(self, filename, filename2, variable,
                 latrange=(-90, 90),
                 lonrange=(-360, 360),
                 depthrange=(0, 0),
                 **kwargs):

        params = kwargs.get('params', None)
        self.params = params

        if not os.access(filename, os.R_OK):
            filename=filename2
        if not os.access(filename, os.R_OK):
                raise FileNotFound(filename)

        with Dataset(filename) as nc:
            self.time = self.get_time(nc.variables)
            self.time_units = self.get_time_unit(nc.variables)
            lats = self.get_lats(nc.variables)
            lons = self.get_lons(nc.variables)
            depths = self.get_depths(nc.variables)

            var = self.get_variable(nc.variables, variable)
            var = self.load_data(var)

            if lons[0] < 0:
                #shifting grid cause data unmasked
                var, lons = shiftgrid(0, var, lons)

            if lats[0] > lats[-1]:
                flippedlats = np.flipud(lats)
                indexes = self.get_indexes(var,
                                       (flippedlats, latrange),
                                       (lons, lonrange),
                                       (depths, depthrange))

            else:
                indexes = self.get_indexes(var,
                                       (lats, latrange),
                                       (lons, lonrange),
                                       (depths, depthrange))

            (lat_idx1, lat_idx2), (lon_idx1, lon_idx2), \
                                  (depth_idx1, depth_idx2) = indexes
            if lats[0] > lats[-1]:
                lat_idx1r = lat_idx1
                lat_idx2r = lat_idx2
                lat_idx1 = lats.size - lat_idx2r
                lat_idx2 = lats.size - lat_idx1r

            # subset the dimension arrays
            self.lats = lats[lat_idx1:lat_idx2:self.GRID_SPACING]
            self.lons = lons[lon_idx1:lon_idx2:self.GRID_SPACING]
            self.depths = depths[depth_idx1:depth_idx2]

            data = self.clip_data(var, (lat_idx1, lat_idx2), \
                                       (lon_idx1, lon_idx2), \
                                       (depth_idx1, depth_idx2))

            self.data = np.squeeze(data)
#            nc.close()

    def _get_variable(self, variables, options):
        """
        Generic routine to try and load a variable from a list of @options
        """

        for v in options:
            try:
                return variables[v][:]
            except KeyError:
                pass

        raise GridWrongFormat("No variable in choices: %s" % options)

    def get_time(self, variables):
        """
        Retrieve time array from the dataset
        """
        if len(self.TIME_VARIABLE):
            return self._get_variable(variables, self.TIME_VARIABLE)
        else:
            return [0.]

    def get_time_unit(self, variables):
        """
        Retrieve time unit from the dataset
        """
        if len(self.TIME_VARIABLE):
            # times = self._get_variable(variables, self.TIME_VARIABLE)[:]
            units = variables['time'].units
            return units
        else:
            return ""

    def get_lats(self, variables):
        """
        Retrieve the latitudes for a dataset.
        """

        return self._get_variable(variables, self.LATS_VARIABLE)

    def get_lons(self, variables):
        """
        Retrieve the longitudes for a dataset.
        """

        return self._get_variable(variables, self.LONS_VARIABLE)

    def get_depths(self, variables):
        """
        Implement to retrieve the depths for a dataset.
        """

        return [0.]

    def get_indexes(self, variable, *args):
        """
        Get the subsetting indexes for any number of datasets, passed as an
        iterable of elements (dataset, (min, max)).

        e.g. (lat_idx1, lat_idx2), (lon_idx1, lon_idx2) = \
            get_indexes(variable,
                        (lats, (latmin, latmax)),
                        (lons, (lonmin, lonmax)))
        """

        return [get_subset_idxs(data, min, max)
                for data, (min, max) in args]

    def get_variable(self, variables, variable):
        """
        Retrieve @variable
        """

        try:
            return variables[variable]
        except KeyError as e:
            raise GridWrongFormat(e)
 
    def clip_data(self, data, (lat_idx1, lat_idx2),
                                  (lon_idx1, lon_idx2),
                                  (depth_idx1, depth_idx2)):
        ndim = len(data.shape)
        if ndim == 3:
            return data[depth_idx1:depth_idx2,
                            lat_idx1:lat_idx2:self.GRID_SPACING,
                            lon_idx1:lon_idx2:self.GRID_SPACING]
        elif ndim == 2: 
            return data[lat_idx1:lat_idx2:self.GRID_SPACING,
                        lon_idx1:lon_idx2:self.GRID_SPACING]
        else:
            raise GridWrongFormat()

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
            return variable[0]
        elif ndim == 2:
            # data arranged lat, lon
            return variable
        else:
            raise GridWrongFormat()

class Gridset(Grid):
    """
    Generic accessor for sets of grids where grids are separated
    temporally in different files.
    """

    #SUFFIX = '.nc' GAS

    apply_to = util.Parameterise(Grid)

    def __init__(self, path, variable, period,
                       #prefix=None, suffix=None, date=None, **kwargs):
                       prefix=None, suffix=None, suffix2=None, date=None, **kwargs):

        assert prefix is not None
        assert suffix is not None
        assert suffix2 is not None 
        assert date is not None

        if variable in ("sst", "anom") and period == "weekly":
            weekdays = util.getWeekDays(date)
            date = weekdays[0]

        filename = self.get_filename(path, prefix, suffix, date, period)
        filename2 =self.get_filename(path, prefix, suffix2, date, period)
        #Grid.__init__(self, filename, variable, **kwargs)
        Grid.__init__(self, filename, filename2, variable, **kwargs)

    def get_filename(self, path, prefix, suffix, date, period):
        """
        Returns the filename for a grid file given the specified @path,
        @prefix, @date and @period of the file.
        """
        return os.path.join(path,
                            '%s%s%s' % (
                            prefix,
                            self.get_filename_date(date,
                                                   params=dict(period=period)),
                            suffix))

#    @apply_to(period='daily')
    def get_filename_date(self, date, **kwargs):
        date_string = ''
        period =  kwargs.get('params')['period']
        if period == 'daily':
            date_string = date.strftime('%Y%m%d')
        elif period == 'weekly':
            base_date = datetime.date(1981, 9, 01)
            weeknumber = util.weeks_between(base_date, date)
            weeknumber = '%02d' % weeknumber
            date_string = date.strftime('%Y%m') + '_week_' + str(weeknumber)
        elif period == 'monthly':
            date_string =  date.strftime('%Y%m')
        elif period == '3monthly':
            date_string = self._get_filename_date(date, 3)
        elif period == '6monthly':
            date_string = self._get_filename_date(date, 6)
        elif period == '12monthly':
            date_string = self._get_filename_date(date, 12)
        return date_string


#    @apply_to(period='monthly')
    #def get_filename_date(self, date, **kwargs):

    def _get_filename_date(self, date, nmonths):
        months = getMonths(date, nmonths)
        return '%imthavg_%s_%s' % (nmonths,
                                   months[0].strftime('%Y%m'),
                                   months[-1].strftime('%Y%m'))

#    @apply_to(period='3monthly')
#    def get_filename_date(self, date, **kwargs):
#        return self._get_filename_date(date, 3)
#
#    @apply_to(period='6monthly')
#    def get_filename_date(self, date, **kwargs):
#        return self._get_filename_date(date, 6)
#
#    @apply_to(period='12monthly')
#    def get_filename_date(self, date, **kwargs):
#        return self._get_filename_date(date, 12)
