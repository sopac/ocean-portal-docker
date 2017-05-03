#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import csv
import datetime
import os
import urllib

import pytest

from ocean.datasets.sealevel import Dataset
from ocean.datasets import ValidationError
from ocean.tests import util

def test_validate_tid():
    qs = urllib.urlencode({
        'dataset': 'sealevel',
        'variable': 'gauge',
        'plot': 'ts',
        'tidalGaugeId': 'IDO70062',
        'period': 'monthly',
    })

    os.environ['QUERY_STRING'] = qs

    params = Dataset.parse()

    print params

def test_validate_tid_bad():
    qs = urllib.urlencode({
        'dataset': 'sealevel',
        'variable': 'gauge',
        'plot': 'ts',
        'tidalGaugeId': 'NOTATID', # bad value
        'period': 'monthly',
    })

    os.environ['QUERY_STRING'] = qs

    with pytest.raises(ValidationError):
        Dataset.parse()

def test_gauge_ts(report):
    util.clear_cache('SEA')

    params = {
        'variable': 'gauge',
        'plot': 'ts',
        'period': 'monthly',
        'tidalGaugeId': 'IDO70062',
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert 'error' not in r
    assert 'tidimg' in r
    assert 'tidtxt' in r
    assert len(r) == 2

    report(params, r['tidimg'])

    fn = util.get_file_from_url(r['tidtxt'])

    assert os.path.exists(fn)

    with open(fn) as f:
        reader = csv.reader(f)

        for i in xrange(3):
            preamble, = reader.next()

            assert preamble.startswith('#')

        headers = reader.next()
        row = reader.next()

        assert len(headers) == len(row)
        assert row == map(str, [2, 1993, 6241, 479, 0.337, 0.961, 0.642, 0.187])

def test_surface_alt(report):
    util.clear_cache('SEA')

    params = {
        'variable': 'alt',
        'plot': 'map',
        'period': 'monthly',
        'date': datetime.date(2000, 2, 1),
        'area': 'pac',
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert 'error' not in r
    assert 'img' in r
    assert 'altimg' not in r

    assert 'alt' in r['img']

    report(params, r['img'])

def test_alt_ts(report):
    util.clear_cache('SEA')

    params = {
        'variable': 'alt',
        'plot': 'ts',
        'period': 'monthly',
        'lat': -30.,
        'lon': 160.,
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert 'error' not in r
    assert 'img' not in r
    assert 'altimg' in r

    assert 'alt' in r['altimg']

    report(params, r['altimg'])

def test_surface_rec(report):
    util.clear_cache('SEA')

    params = {
        'variable': 'rec',
        'plot': 'map',
        'period': 'monthly',
        'date': datetime.date(1950, 2, 1),
        'area': 'pac',
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert 'error' not in r
    assert 'img' in r
    assert 'recimg' not in r

    assert 'rec' in r['img']

    report(params, r['img'])

def test_rec_ts(report):
    util.clear_cache('SEA')

    params = {
        'variable': 'rec',
        'plot': 'ts',
        'period': 'monthly',
        'lat': -30.,
        'lon': 160.,
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert 'error' not in r
    assert 'img' not in r
    assert 'recimg' in r

    assert 'rec' in r['recimg']

    report(params, r['recimg'])

@pytest.mark.bug224
def test_alt_range_wrapping():
    params = {
        'variable': 'alt',
        'plot': 'ts',
        'period': 'monthly',
        'lat': -12.270,
        'lon': -163.475
    }

    ds = Dataset()
    r = ds.process(params)

    assert 'error' not in r

@pytest.mark.bug222
def test_land_error():

    params = {
        'variable': 'alt',
        'plot': 'ts',
        'period': 'monthly',
        'lat': -23.,
        'lon': 146.,
    }

    ds = Dataset()

    from ocean.netcdf.extractor import LandError

    with pytest.raises(LandError):
        ds.process(params)
