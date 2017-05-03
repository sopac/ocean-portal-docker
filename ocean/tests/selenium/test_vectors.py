#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import time

import pytest
from selenium.common.exceptions import InvalidSelectorException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from ocean.tests import util

from uiutil import *
from test_map import select_region

def test_display_gauges(b, url):
    b.get(url)

    b.select_param('variable', 'Tidal Gauge')
    time.sleep(4) # wait for the map to stabilise
    b.wait(jquery('svg circle'))

    markers = b.find_elements_by_jquery('svg circle')

    print markers

    # check we have the right number of markers
    assert len(markers) == 13

    for m in markers:
        assert m.is_displayed()
        assert m.get_attribute('stroke') == 'white'
        assert m.get_attribute('fill') == 'black'

def test_click_gauge(b, url):
    b.get(url)

    b.select_param('variable', 'Tidal Gauge')
    time.sleep(4) # wait for the map to stabilise
    b.wait(jquery('svg circle'))

    marker = b.find_element_by_jquery('svg circle:first')

    assert marker.get_attribute('stroke') == 'white'

    marker.click()

    assert marker.get_attribute('stroke') == 'red'

    # this will be the first value in the config file
    input = b.find_element_by_id('tidalgauge')
    assert input.get_attribute('value') == "Fiji - Suva"

    input = b.find_element_by_id('tgId')
    assert input.get_attribute('value') == 'IDO70063'

    util.clear_cache('SEA')
    b.submit()
    b.wait(output('SEA'))

@pytest.mark.bug200
def test_hover_gauge(b, url):
    b.get(url)

    b.select_param('variable', 'Tidal Gauge')
    time.sleep(4) # wait for the map to stabilise
    b.wait(jquery('svg circle'))

    marker = b.find_element_by_jquery('svg circle:first')

    chain = ActionChains(b)
    chain.move_to_element(marker)
    chain.perform()

    elems = b.find_elements_by_jquery('svg text')
    assert len(elems) == 1
    assert elems[0].text == "Fiji - Suva"

def test_gauge_offscreen(b, url):
    b.get(url)

    b.select_param('variable', 'Tidal Gauge')
    select_region(b, 'niue')

    with pytest.raises(InvalidSelectorException):
        # with all the circles offscreen there's nothing to select
        b.find_element_by_jquery('svg circle')

    select_region(b, 'samoa')
    assert len(b.find_elements_by_jquery('svg circle')) > 0

def pan_map(b, offsetx, offsety):
    map = b.find_element_by_id('map')

    act = ActionChains(b)
    act.move_to_element(map)
    act.click_and_hold()
    act.move_by_offset(offsetx, offsety)
    act.release()
    act.perform()

    time.sleep(1)

@pytest.mark.bug183
@pytest.mark.bug195
@pytest.mark.unstable
def test_gauge_bug195(b, url):
    b.get(url)

    b.select_param('variable', 'Tidal Gauge')
    b.wait(jquery('svg circle'))
    select_region(b, 'fiji')

    assert len(b.find_elements_by_jquery('svg circle')) == 2

    LEFT_PAN = 50
    RIGHT_PAN = 375

    pan_map(b, -LEFT_PAN, 0)

    assert len(b.find_elements_by_jquery('svg circle')) == 2

    pan_map(b, LEFT_PAN + RIGHT_PAN, 0)

    assert len(b.find_elements_by_jquery('svg circle')) == 2

@pytest.mark.bug183
@pytest.mark.unstable
@pytest.mark.parametrize(('lat', 'lon'), [
    (-18, 177),
    (-16, -179),
])
def test_display_markers_big_movements(b, url, lat, lon):
    b.get(url)

    b.select_param('variable', 'Salinity')
    b.select_param('plottype', 'Sub-surface Cross-section')

    b.find_element_by_id('latitude').send_keys(str(lat) + Keys.TAB)
    b.find_element_by_id('longitude').send_keys(str(lon) + Keys.TAB)

    time.sleep(1)

    # svg > polygon is important, else you match both the point and the
    # definition
    assert len(b.find_elements_by_jquery('svg > polygon')) == 1

    select_region(b, 'fiji')
    assert len(b.find_elements_by_jquery('svg > polygon')) == 1

    # asymmetric because it makes the test a little more stable
    LEFT_PAN = -250
    RIGHT_PAN = 300

    pan_map(b, LEFT_PAN, 0)
    assert len(b.find_elements_by_jquery('svg > polygon')) == 0

    pan_map(b, RIGHT_PAN, 0)
    assert len(b.find_elements_by_jquery('svg > polygon')) == 1

    pan_map(b, RIGHT_PAN, 0)
    assert len(b.find_elements_by_jquery('svg > polygon')) == 0

    pan_map(b, LEFT_PAN, 0)
    assert len(b.find_elements_by_jquery('svg > polygon')) == 1

@pytest.mark.bug183
@pytest.mark.parametrize(('lat', 'lon'), [
    (-18, 177),
    (-16, -178),
])
def test_display_markers_small_movements(b, url, lat, lon):
    b.get(url)

    select_region(b, 'fiji')
    b.select_param('variable', 'Salinity')
    b.select_param('plottype', 'Sub-surface Cross-section')

    b.find_element_by_id('latitude').send_keys(str(lat) + Keys.TAB)
    b.find_element_by_id('longitude').send_keys(str(lon) + Keys.TAB)

    time.sleep(1)

    # svg > polygon is important, else you match both the point and the
    # definition
    assert len(b.find_elements_by_jquery('svg > polygon')) == 1

    LEFT_PAN = 20

    pan_map(b, -LEFT_PAN, 0)
    assert len(b.find_elements_by_jquery('svg > polygon')) == 1

    pan_map(b, LEFT_PAN, 0)
    assert len(b.find_elements_by_jquery('svg > polygon')) == 1

    pan_map(b, LEFT_PAN, 0)
    assert len(b.find_elements_by_jquery('svg > polygon')) == 1

    pan_map(b, -LEFT_PAN, 0)
    assert len(b.find_elements_by_jquery('svg > polygon')) == 1

@pytest.mark.parametrize(('lon'), [
    (177),
    (184),
    (-178),
    (-215),
])
def test_lon_clamping(b, url, lon):
    b.get(url)

    b.select_param('variable', 'Salinity')
    b.select_param('plottype', 'Sub-surface Cross-section')

    # this needs to be valid to attempt parsing
    b.find_element_by_id('latitude').send_keys('0')

    longitude = b.find_element_by_id('longitude')
    longitude.send_keys(str(lon) + Keys.TAB)

    lonout = float(longitude.get_attribute('value'))
    assert -180 < lonout < 180
    assert lonout == (lon + 180) % 360 - 180
