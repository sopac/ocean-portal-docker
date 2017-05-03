#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import datetime

import pytest

from ocean.datasets.bran import Dataset
from ocean.tests import util

"""
Tests that take the parameter @period will be run for all periods configured
in the Dataset class.
"""

def test_surface(report, variable, period):
    util.clear_cache('BRN')

    params = {
        'area': 'fiji',
        'date': datetime.date(2000, 1, 1),
        'period': period,
        'variable': variable,
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert not 'error' in r
    assert 'img' in r

    report(params, r['img'])

@pytest.mark.parametrize(('var'), [
    'temp',
    'salt',
])
def test_xsection(report, var, period):
    util.clear_cache('BRN')

    params = {
        'area': 'pac',
        'date': datetime.date(2000, 1, 1),
        'period': period,
        'variable': var,
        'lat': -30.,
        'lon': 160.,
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert not 'error' in r
    assert 'img' in r

    report(params, r['img'])

@pytest.mark.parametrize(('lat', 'lon'), [
    (-30., 160.),
    (-30., 150.),
    (-20., 160.),
])
def test_crosssection_zonal_meridional(report, lat, lon):
    util.clear_cache('BRN')

    params = {
        'area': 'pac',
        'date': datetime.date(2006, 1, 1),
        'period': 'monthly',
        'variable': 'temp',
        'lat': lat,
        'lon': lon,
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert not 'error' in r
    assert 'img' in r

    assert ('%i' % abs(lat)) in r['img']
    assert ('%i' % abs(lon)) in r['img']

    report(params, r['img'])
