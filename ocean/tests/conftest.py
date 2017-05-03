#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import pytest

def pytest_addoption(parser):
    parser.addoption('--skip-unstable', action='store_true',
                     dest='skip_unstable', help="Skip unstable tests")

def pytest_generate_tests(__multicall__, metafunc):
    """
    Supports parametrised tests using generate_*() fns.

    Taken from GFE test suite.
    """

    __multicall__.execute()

    name = metafunc.function.__name__.replace('test_', 'generate_')
    fn = getattr(metafunc.module, name, None)
    if fn:
        fn(metafunc)

def pytest_runtest_setup(item):
    if 'unstable' in item.keywords and item.config.option.skip_unstable:
        pytest.skip("Skipping unstable test")
