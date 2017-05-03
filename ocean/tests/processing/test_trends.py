#!/usr/bin/python
#
# (c) 2013 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import datetime

import pytest
import numpy as np

from ocean.datasets.reynolds import Plotter
from ocean.processing import trends

@pytest.mark.parametrize(('period'), [
    'yearly',
    '3monthly',
    'monthly',
])
def test_stacked_grid(period):
    years, lats, lons, data = trends.stack_grids(Plotter(), base_year=1982)

    # FIXME: how do we ensure we're loading the right grids

    nyears = datetime.date.today().year - 1982

    assert years.ndim == lats.ndim == lons.ndim == 1
    assert len(years) == nyears
    assert len(lats) == 180 / 0.25 # Reynolds is 0.25 degree bins
    assert len(lons) == 360 / 0.25
    assert data.shape == (nyears, len(lats), len(lons))

def test_calculate_trends():
    years, lats, lons, data = trends.stack_grids(Plotter(), base_year=1982)

    t = trends.calculate_spatial_trends(years, data)

    assert t.shape == (2, len(lats), len(lons))

    # test a single point ourselves
    p = np.polyfit(years, data[:, 300, 300], 1)

    assert p.shape == t[:, 300, 300].shape == (2,)
    assert np.all(t[:, 300, 300] == p)

