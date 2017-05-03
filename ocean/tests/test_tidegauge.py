#
# (c) 2013 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import datetime

import numpy as np
from numpy.testing import assert_almost_equal

from ocean.datasets.sealevel import TideGauge

def test_load_data():
    data = TideGauge('IDO70052')

    date = data.date[0]
    assert date.year == 1993 and \
           date.month == 5 and \
           date.day == 1

    assert data.date[-1] >= datetime.date(year=2013, month=1, day=1)

    # there were 237 records as of Feb 2013
    assert len(data) >= 237

    # apply some tests to the first 237 records
    data = data[:237]

    assert data.gaps.sum() == 36560
    assert data.good.sum() == 1695280
    assert_almost_equal(data.minimum.min(), -0.238)
    assert_almost_equal(data.maximum.max(), 2.405)
    assert_almost_equal(data.mean_.mean(), 1.054, 3)

def test_load_data2():
    # this file is annoyingly formatted
    data = TideGauge('IDO70062')

    date = data.date[0]
    assert date.year == 1993 and \
           date.month == 2 and \
           date.day == 1

    assert data.date[-1] >= datetime.date(year=2013, month=1, day=1)
