#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import datetime

import pytest

from ocean.datasets.ersst import Dataset
from ocean.tests import util

"""
Test plots for all variables and periods
"""

def test_ersst(report, variable, period):
    util.clear_cache('ERA')

    if variable == 'trend' and period == '12monthly':
        pytest.skip("Not useful")
    elif variable != 'trend' and period == 'yearly':
        pytest.skip("No data for this var/period")

    params = {
        'area': 'pac',
        'date': datetime.date(2000, 1, 1),
        'period': period,
        'variable': variable,
        'baseYear': 1950,
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert not 'error' in r
    assert 'img' in r

    report(params, r['img'])
