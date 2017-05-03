#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os.path
import subprocess
import json

import pytest

import ocean

def get_resource(*args):
    return os.path.join(ocean.__path__[0], '..', *args)

def test_html_validates():
    """
    This test just applies a basic lint, it doesn't yet check for conformance.
    """

    path = get_resource('html', 'compmap.html')
    subprocess.check_call(['xmllint', path])

@pytest.mark.parametrize(('file'), [
    ('datasets.json'),
    ('portals.json'),
    ('vargroups.json'),
])
def test_json_validates(file):
    """
    This test just tries to load the JSON file with the Python JSON module.
    It doesn't run a proper lint or check for JSON conformance.
    """

    path = get_resource('config', 'comp', file)
    with open(path, 'r') as f:
        json.load(f)
