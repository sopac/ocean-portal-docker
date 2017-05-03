#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import datetime

import pytest

from ocean.datasets.ww3 import Dataset
from ocean.tests import util

"""
Tests that take the parameter @period will be run for all periods configured
in the Dataset class.
"""

def test_plot(report, variable, period):
    util.clear_cache('WAV')

    params = {
        'date': datetime.date(2000, 1, 1),
        'period': period,
        'variable': variable,
        'lllat': -30.,
        'lllon': 160.,
        'urlat': -30.,
        'urlon': 160.,
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert not 'error' in r
    assert 'img' in r

    report(params, r['img'])

def test_land_error():

    params = {
        'date': datetime.date(2000, 1, 1),
        'period': 'monthly',
        'variable': 'Dm',
        'lllat': -23.,
        'lllon': 146.,
        'urlat': -23.,
        'urlon': 146.,
    }

    ds = Dataset()

    from ocean.netcdf.extractor import LandError

    with pytest.raises(LandError):
        ds.process(params)

def test_wrapping():
    params = {
        'date':  datetime.date(2000, 1, 1),
        'period': 'monthly',
        'variable': 'Dm',
        'lllat': -7.383,
        'lllon': -179.756,
        'urlat': -7.383,
        'urlon': -179.756,
    }

    ds = Dataset()
    r = ds.process(params)

    assert not 'error' in r
    assert 'img' in r
