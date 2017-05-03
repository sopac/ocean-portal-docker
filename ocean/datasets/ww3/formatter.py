#!/usr/bin/env python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Jason Smith <jason.smith@bom.gov.au>

def nameformat(lat,lon):

    #if lat >= 0:
     #   latst = '%s%s' % ('+',lat)
    #if lon >= 0:
      #  lonst = '%s%s' % ('+',lon)

    latstr = '%+08.3f' % float(lat)
    lonstr = '%+08.3f' % float(lon)

    return latstr, lonstr

def NESWformat(lat,lon):
    lat = round(float(lat),2)
    lon = round(float(lon),2)
    latstr = str(lat)
    lonstr = str(lon)

    if lat >= 0:
        latstr = '%s %s' % (lat,'N')

    if lon >= 0:
        lonstr = '%s %s' % (lon,'E')

    if lat < 0:
        laty = abs(lat)
        latstr = '%s %s' % (laty,'S')

    if lon < 0:
        lony = abs(lon)
        lonstr = '%s %s' % (lony,'W')

    return latstr,lonstr
