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

from ocean.datasets.msla import Dataset
from ocean.datasets import ValidationError, MissingParameter
from ocean.tests import util

def test_msla_validate_params_incomplete(report):
    util.clear_cache('SEA')

    params = {
        'variable': 'sla',
        'plot': 'map',
        'period': 'daily', 
        'date': datetime.date(2015, 7, 9),       
    }
    
    ds = Dataset()
    with pytest.raises(MissingParameter) as excinfo:
        r = ds.process(params)
    assert excinfo.value.message == "Missing parameter 'area'"      
    
def test_surface_msla(report):
    util.clear_cache('SEA')

    params = {
        'variable': 'sla',
        'plot': 'map',
        'period': 'daily',
        'date': datetime.date(2015, 7, 6),
        'area': 'pac',
    }
    
    ds = Dataset()
    r = ds.process(params)

    assert 'error' not in r
    assert 'img' in r
    assert 'mapimg' in r
    assert 'scale' in r

    report(params, r['img'])