#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#         All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

"""
Tests should be defined as:
    def test_badger(b, url, ...):
        b.get(url)
        ...
"""

import os

import pytest
from selenium import webdriver

from uiutil import MapPortalDriver

browsers = {
    'firefox': webdriver.Firefox,
    # 'chrome': webdriver.Chrome,
}

def pytest_addoption(parser):
    # add a --url option which overrides the value of the 'url' parameter
    # passed to tests
    parser.addoption('--url', action='store',
                     default='http://localhost/portal/compmap.html')
    parser.addoption('--browsers', action='store',
                     default=browsers.keys())

@pytest.fixture(scope='session',
                params=browsers.keys())
def driver(request):
    if 'DISPLAY' not in os.environ:
        pytest.skip('Test requires display server (export DISPLAY)')

    if request.param not in request.config.option.browsers:
        pytest.skip('Unrequested test, run with --browser %s' % request.param)

    b = MapPortalDriver(browsers[request.param])()

    request.addfinalizer(lambda *args: b.quit())

    return b

@pytest.fixture
def b(driver):
    b = driver
    b.set_window_size(1200, 800)

    return b

@pytest.fixture(scope='session')
def url(request):
    return request.config.option.url
