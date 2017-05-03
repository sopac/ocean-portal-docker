#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

"""
Tests of core frontend functionality.

Exhaustive tests of the datasets can be found in test_datasets.py.

The function arguments @b and @url are provided by fixtures defined in
conftest.py
"""

import time

import pytest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from ocean.tests import util

from uiutil import *

def test_load(b, url):
    b.get(url)

    time.sleep(1)

    # check Bathymetry is selected and enabled
    elem = b.find_element_by_xpath('//input[@value="Bathymetry"]')
    assert elem.get_attribute('checked')
    assert elem.get_attribute('disabled') is None

    # check Output is unselected and disabled
    elem = b.find_element_by_xpath('//input[@value="Output"]')
    assert elem.get_attribute('checked') is None
    assert elem.get_attribute('disabled')

def test_mean_sst_monthly(b, url):
    b.get(url)

    util.clear_cache('ERA')

    b.select_param('variable', 'Mean Temperature')
    b.ensure_selected('plottype', 'Surface Map', noptions=2)
    b.select_param('period', 'Monthly')
    b.select_param('month', 'January')
    b.select_param('year', '2012')

    assert b.select_contains('dataset', ['reynolds', 'ersst'])
    b.select_param('dataset', 'ERSST')

    b.submit()

    b.wait(output('ERA'))

    # check Bathymetry is enabled but not selected
    elem = b.find_element_by_xpath('//input[@value="Bathymetry"]')
    assert elem.get_attribute('checked') is None
    assert elem.get_attribute('disabled') is None

    # check Output is enabled and selected
    elem = b.find_element_by_xpath('//input[@value="Output"]')
    assert elem.get_attribute('checked')
    assert elem.get_attribute('disabled') is None

def test_wave_watch_rose(b, url):
    b.get(url)

    util.clear_cache('WAV')

    b.select_param('variable', 'Mean Wave Direction')
    b.ensure_selected('plottype', 'Waverose')
    b.ensure_selected('period', 'Monthly')
    b.select_param('month', 'October') # September and October had a bug
    b.ensure_selected('dataset', 'WaveWatch III')

    elem = b.find_element_by_id('latitude')
    elem.send_keys("-45")
    elem.send_keys(Keys.TAB)

    elem = b.switch_to_active_element()
    elem.send_keys("145")

    b.submit()

    b.wait(output('WAV'))

    # check Bathymetry is selected and enabled
    elem = b.find_element_by_xpath('//input[@value="Bathymetry"]')
    assert elem.get_attribute('checked')
    assert elem.get_attribute('disabled') is None

    # check Output is unselected and disabled
    elem = b.find_element_by_xpath('//input[@value="Output"]')
    assert elem.get_attribute('checked') is None
    assert elem.get_attribute('disabled')

def test_removing_outputs(b, url):
    """
    This test adds a surface output, and then a graph output.

    It then removes the surface output.
    """

    b.get(url)

    # create a surface plot
    b.select_param('variable', 'Mean Temperature')
    b.ensure_selected('plottype', 'Surface Map', noptions=2)
    b.select_param('period', 'Monthly')
    b.select_param('month', 'January')
    b.select_param('year', '2012')

    assert b.select_contains('dataset', ['reynolds', 'ersst'])
    b.select_param('dataset', 'ERSST')

    b.submit()

    b.wait(output('ERA'))

    # check Bathymetry is enabled but not selected
    elem = b.find_element_by_xpath('//input[@value="Bathymetry"]')
    assert elem.get_attribute('checked') is None
    assert elem.get_attribute('disabled') is None

    # check Output is enabled and selected
    elem = b.find_element_by_xpath('//input[@value="Output"]')
    assert elem.get_attribute('checked')
    assert elem.get_attribute('disabled') is None

    # create a non-surface plot
    b.select_param('variable', 'Mean Wave Direction')
    b.ensure_selected('plottype', 'Waverose')
    b.ensure_selected('period', 'Monthly')
    b.select_param('month', 'October') # September and October had a bug
    b.ensure_selected('dataset', 'WaveWatch III')

    elem = b.find_element_by_id('latitude')
    elem.send_keys("-45")
    elem.send_keys(Keys.TAB)

    elem = b.switch_to_active_element()
    elem.send_keys("145")

    b.submit()

    b.wait(output('WAV'))

    # check Bathymetry is selected and enabled
    elem = b.find_element_by_xpath('//input[@value="Bathymetry"]')
    assert elem.get_attribute('checked')
    assert elem.get_attribute('disabled') is None

    # check Output is unselected but enabled
    elem = b.find_element_by_xpath('//input[@value="Output"]')
    assert elem.get_attribute('checked') is None
    assert elem.get_attribute('disabled') is None

    b.wait(animation_finished)

    # check the # of outputs
    elems = b.find_elements_by_jquery('.outputgroup')
    assert len(elems) == 2

    # delete the 2nd output
    elem = b.find_element_by_jquery('.outputgroup ~ .outputgroup')
    print elem, elem.location
    action = ActionChains(b)
    action.move_to_element(elem)
    action.click(on_element=elem.find_element_by_css_selector('.close-button'))
    action.perform()

    b.wait(animation_finished)

    # check the # of outputs
    elems = b.find_elements_by_jquery('.outputgroup')
    assert len(elems) == 1

    # check Bathymetry is selected and enabled
    elem = b.find_element_by_xpath('//input[@value="Bathymetry"]')
    assert elem.get_attribute('checked')
    assert elem.get_attribute('disabled') is None

    # check Output is unselected and disabled
    elem = b.find_element_by_xpath('//input[@value="Output"]')
    assert elem.get_attribute('checked') is None
    assert elem.get_attribute('disabled')

@pytest.mark.bug201
@pytest.mark.parametrize(('variable', 'min', 'max'), [
    ('Reconstruction', '1950', '2009'),
    ('Altimetry', '1993', '2012'),
    ('Anomalies', '1950', '2012'),
])
def test_date_range(b, url, variable, min, max):
    """
    Make sure we have the full range of the data set.
    """

    b.get(url)

    b.select_param('variable', variable)
    b.select_param('plottype', 'Surface Map')
    b.select_param('period', 'Monthly')

    options = b.find_elements_by_jquery('#year option')
    assert options[0].get_attribute('value') == min
    assert options[-1].get_attribute('value') == max

@pytest.mark.bug204
def test_date_range_multi_month_periods_1(b, url):
    b.get(url)

    b.select_param('variable', 'Mean Temperature')
    b.select_param('plottype', 'Sub-surface Cross-section')
    b.select_param('period', '3 monthly')
    b.select_param('year', '1993')

    b.ensure_selected('dataset', 'BRAN')

    elem = b.find_element_by_jquery('#year option:first')
    assert elem.get_attribute('value') == '1993'

    elem = b.find_element_by_jquery('#month option:first')
    assert elem.get_attribute('value') == '2' # months enumerate from 0 in JS

@pytest.mark.bug204
def test_date_range_multi_month_periods_2(b, url):
    b.get(url)

    b.select_param('variable', 'Mean Temperature')
    b.select_param('plottype', 'Surface Map')
    b.select_param('period', '3 monthly')
    b.select_param('year', '1993')
    b.select_param('month', 'Nov 92 - Jan 93')

    elems = b.find_elements_by_jquery('#dataset option')
    assert 'bran' not in map(lambda e: e.get_attribute('value'), elems)

def test_date_range_years_present_not_present(b, url):
    b.get(url)

    # select a thing where we do specify the year
    b.select_param('variable', 'Anomalies')
    b.select_param('plottype', 'Surface Map')
    b.select_param('period', '3 monthly')
    b.select_param('year', '2012')
    b.select_param('month', 'Dec 11 - Feb 12')

    # select a thing where we don't
    b.select_param('variable', 'Trend')
    b.select_param('month', 'Dec - Feb')

    assert len(b.find_elements_by_jquery('#year:visible')) == 0
