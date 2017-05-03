#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import time
from urlparse import urlparse, parse_qs

import pytest

from ocean.config.regionConfig import regions
from ocean.tests import util

from uiutil import *

# PAC_REGIONS = filter(lambda r: regions[r][0] == 'pac', regions.keys())
PAC_REGIONS = ['samoa', 'fiji', 'fsm']

def coerce_mapext(p):
    return map(float, p[0].split(' '))

def get_bounds(b):

    def _get_mapext(e):
        params = parse_qs(urlparse(e.get_attribute('src')).query)
        return coerce_mapext(params['mapext'])

    mapexts = map(_get_mapext, b.find_elements_by_jquery('.olTileImage'))

    def _min(a, b):
        if a < 0:
            a += 360
        if b < 0:
            b += 360
        return min(a, b)

    def _max(a, b):
        if a < 0:
            a += 360
        if b < 0:
            b += 360
        return max(a, b)

    def _get_bounds(a, b):
        m = (_min, min, _max, max)
        c = zip(a, b)

        return map(lambda (f, p): f(*p), zip(m, c))

    return reduce(_get_bounds, mapexts, [ 1000, 1000, -1000, -1000 ])

def region_on_screen(b, region):
    lllon, lllat, urlon, urlat = get_bounds(b)
    rb = regions[region][1]

    print "bounds", lllon, lllat, urlon, urlat
    print "region", rb

    # region box should be within the region shown on the screen
    assert rb['llcrnrlon'] >= lllon and \
           rb['llcrnrlat'] >= lllat and \
           rb['urcrnrlon'] <= urlon and \
           rb['urcrnrlat'] <= urlat

    return True

def select_region(b, region):
    b.select_param('region', regions[region][2])
    # FIXME: slow
    time.sleep(4) # wait for the map to stabilise

@pytest.mark.parametrize(('region'), PAC_REGIONS)
def test_select_region(b, url, region):
    b.get(url)

    select_region(b, region)
    assert region_on_screen(b, region)

@pytest.mark.parametrize(('region1', 'region2'),
    [ (region1, region2) for region1 in PAC_REGIONS
                         for region2 in PAC_REGIONS
                         if region1 != region2 ])
def test_changing_regions(b, url, region1, region2):
    b.get(url)

    select_region(b, region1)
    assert region_on_screen(b, region1)

    select_region(b, region2)
    assert region_on_screen(b, region2)

    select_region(b, region1)
    assert region_on_screen(b, region1)

@pytest.mark.bug197
@pytest.mark.parametrize(('region1', 'region2'),
    [ (region1, region2) for region1 in PAC_REGIONS
                         for region2 in PAC_REGIONS
                         if region1 != region2 ])
def test_changing_regions_small_map(b, url, region1, region2):

    b.set_window_size(1080, 600)
    b.get(url)

    select_region(b, region1)
    assert region_on_screen(b, region1)

    select_region(b, region2)
    assert region_on_screen(b, region2)

    select_region(b, region1)
    assert region_on_screen(b, region1)
