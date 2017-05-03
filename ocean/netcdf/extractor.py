#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import bisect
import math

import numpy as np
import numpy.ma as ma

from ocean.core import ReportableException

class OutOfDataRange(ReportableException):
    def __init__(self, point, lats, lons):
        ReportableException.__init__(self,
            "The selected location (%.3f,%.3f) is outside the available range (%g, %g)-(%g, %g)" % (
                point[0], point[1], lats[0], lats[-1], lons[0], lons[-1]))

class LandError(ReportableException):
    def __init__(self,
                 msg="no data at this location, please choose another point"):
                # msg="Selected point is on land. Please choose another point."):
        ReportableException.__init__(self, msg)

class Extractor():
    """
    Extract point/rectangular area data.
    """

    _RADIUS = 2

    @classmethod
    def getGridPoint(self, inputLat, inputLon, lats, lons, var,
                     strategy='nearest', validate_range=True):
        """
        Align the input lat/lon to the grid lat/lon. Also returns the index
        of the grid lat/lon.
        """

        gridPointColIndex = 0

        if lats[0] > lats[-1]:
            flippedlats = np.flipud(lats)
            latInsertIndex = bisect.bisect_left(flippedlats, inputLat)
            latInsertIndex = lats.size - latInsertIndex
        else:
            latInsertIndex = bisect.bisect_left(lats, inputLat)
        #latInsertIndex = bisect.bisect_left(lats, inputLat)
        # For lon, first we need to check the lon range in the dataset.
        # if the lon range is from 0 to a number larger
        # than 180, than we should convert the input lon. Otherwise the
        # input lon is fine.

        dataLon = inputLon
        if lons[-1] > 180:
            if inputLon < 0:
                dataLon = inputLon + 360

        nearestPoints = []
        lonInsertIndex = bisect.bisect_left(lons, dataLon)

        #check if the dataset is upside down
        upside_down = lats[0] > lats[-1]
        # check if the dataset wraps around the globe
        dataset_wraps = (np.abs(lons[0] + lons[-1]) % 360) ** 2 <= 25

        if validate_range and \
           ((upside_down and not lats[-1] < inputLat < lats[0]) or \
            (not upside_down and not lats[0] < inputLat < lats[-1]) or \
            (not dataset_wraps and not lons[0] < dataLon < lons[-1])):
            raise OutOfDataRange((inputLat, inputLon), lats, lons)

        # extract a square grid of points size 2r x 2r
        for latIndex in range(latInsertIndex - self._RADIUS,
                              latInsertIndex + self._RADIUS + 1):
            if latIndex < 0 or latIndex >= len(lats):
                # There is no need to wrap the lat, therefore skip till the
                # index is in range
                pass
            else:
                for lonIndex in range(lonInsertIndex - self._RADIUS,
                                      lonInsertIndex + self._RADIUS + 1):
                    if lonIndex < 0 or lonIndex >= len(lons):
                        if dataset_wraps:
                            nearestPoints.append((lonIndex % len(lons),
                                                  latIndex % len(lons)))
                        else:
                            pass
                    else:
                        nearestPoints.append((lonIndex, latIndex))

        # sort the points based on closeness within the grid
        input = (inputLon, inputLat)
        nearestPoints.sort(key=lambda coord: (input[0] - lons[coord[0]]) ** 2 + (input[1] - lats[coord[1]]) ** 2)

        return getattr(self, '_%s_strategy' % strategy)(nearestPoints,
                                                        lats, lons,
                                                        var)

    @classmethod
    def _nearest_strategy(self, sortedNearestPoints, lats, lons, var):
        return ((lats[sortedNearestPoints[0][1]],
                 lons[sortedNearestPoints[0][0]]),
                sortedNearestPoints[0][::-1])

    @classmethod
    def _exhaustive_strategy(self, sortedNearestPoints, lats, lons, var):
        result = self._nearest_strategy(sortedNearestPoints, lats, lons, var)
        for point in sortedNearestPoints:
            if var[point[1], point[0]] is not ma.masked:
                result = ((lats[point[1]], lons[point[0]]),
                          (point[1], point[0]))
                break
        return result

    @classmethod
    def extract(self, data, lats, lons, latTop, latBottom, lonLeft, lonRight):
        """
        Extract an area of data from the gridded data.
        """
        latmin = lats >= latBottom
        latmax = lats <= latTop
        lonmin = lons >= lonLeft
        lonmax = lons <= lonRight

        latrange = latmin & latmax
        lonrange = lonmin & lonmax

        latSlice = sst[latrange]
        extracted = latSlice[:, lonrange]
        return extracted
