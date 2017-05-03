#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import pytest

from ocean.tests import util

from uiutil import *

@pytest.mark.parametrize(('variable'), [
    ('Significant Wave Height',),
    ('Mean Wave Period',),
])
def test_histogram(b, url, variable):
    b.get(url)

    b.select_param('variable', variable)
    b.ensure_selected('plottype', 'Histogram')
    b.select_param('period', 'Monthly')
    b.select_param('month', 'January')

    assert len(b.find_elements_by_jquery('#year:visible')) == 0

    b.ensure_selected('dataset', 'WaveWatch III')

    elem = b.find_element_by_id('latitude')
    elem.send_keys("-45")

    elem = b.find_element_by_id('longitude')
    elem.send_keys("145")

    util.clear_cache('WAV')
    b.submit()
    b.wait(output('WAV'))

@pytest.mark.parametrize(('variable', 'dataset', 'product'), [
    ('Mean Temperature', 'Reynolds', 'REY'),
    ('Anomalies', 'Reynolds', 'REY'),
    ('Deciles', 'Reynolds', 'REY'),
    ('Mean Temperature', 'ERSST', 'ERA'),
    ('Anomalies', 'ERSST', 'ERA'),
    ('Deciles', 'ERSST', 'ERA'),
    ('Mean Temperature', 'BRAN', 'BRN'),
    ('Salinity', 'BRAN', 'BRN'),
    ('Reconstruction', 'Church & White', 'SEA'),
    ('Altimetry', 'Church & White', 'SEA'),
])
def test_surface_maps(b, url, variable, dataset, product):
    b.get(url)

    b.select_param('variable', variable)
    b.select_param('plottype', 'Surface Map')
    b.select_param('period', 'Monthly')
    b.select_param('year', '2000')
    b.select_param('month', 'November')
    b.select_param('dataset', dataset)

    util.clear_cache(product)
    b.submit()
    b.wait(output(product))

@pytest.mark.parametrize(('variable', 'dataset', 'product'), [
    ('Mean Temperature', 'BRAN', 'BRN'),
    ('Salinity', 'BRAN', 'BRN'),
])
def test_cross_sections(b, url, variable, dataset, product):
    b.get(url)

    b.select_param('variable', variable)
    b.select_param('plottype', 'Sub-surface Cross-section')
    b.select_param('period', 'Monthly')
    b.select_param('year', '2000')
    b.select_param('month', 'November')
    b.select_param('dataset', dataset)

    elem = b.find_element_by_id('latitude')
    elem.send_keys("-45")

    elem = b.find_element_by_id('longitude')
    elem.send_keys("145")

    util.clear_cache(product)
    b.submit()
    b.wait(output(product))

def test_currents_bad(b, url):
    """
    This test will fail because the region is too big.
    """

    b.get(url)

    b.select_param('region', 'Pacific Ocean')
    b.select_param('variable', 'Temp & Currents')
    b.ensure_selected('plottype', 'Surface Map')
    b.ensure_selected('period', 'Monthly')
    b.select_param('month', 'March')
    b.select_param('year', '2005')
    b.ensure_selected('dataset', 'BRAN')

    util.clear_cache('BRN')
    b.submit()

    with pytest.raises(FrontendError):
        b.wait(output('BRN'))

@pytest.mark.parametrize(('variable'), [
    ('Temp & Currents',),
    ('Sea Level & Currents',),
])
def test_currents(b, url, variable):
    b.get(url)

    b.select_param('region', 'Fiji')
    b.select_param('variable', variable)
    b.ensure_selected('plottype', 'Surface Map')
    b.ensure_selected('period', 'Monthly')
    b.select_param('month', 'March')
    b.select_param('year', '2005')
    b.ensure_selected('dataset', 'BRAN')

    util.clear_cache('BRN')
    b.submit()
    b.wait(output('BRN'))
