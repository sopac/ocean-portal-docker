#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

"""
Test uiutils
"""

import pytest

from uiutil import *

def test_jquery(b, url):
    b.get(url)

    elems = b.find_elements_by_jquery('#region')
    assert len(elems) == 1

    elem = b.find_element_by_jquery('#region')
    assert elem.tag_name == 'select'
    assert elem.get_attribute('id') == 'region'

    subelems = elem.find_elements_by_jquery('option')
    for e in subelems:
        print e.text

    assert all([ e.tag_name == 'option' for e in subelems ])
    assert all([ b.execute_script(
        '''return $(arguments[0]).parent('select').get();''',
        e)[0].get_attribute('id') == 'region'
        for e in subelems ])
