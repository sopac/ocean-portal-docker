#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os
import os.path
from glob import glob

import pytest

from ocean.config import get_server_config

config = get_server_config()

def clear_cache(product, filetype='*'):
    cachedir = config['outputDir']
    s = os.path.join(cachedir, '%s*.%s' % (product, filetype))

    for d in glob(s):
        try:
            os.unlink(d)
        except IOError:
            raise

def unique(iterable):
    __tracebackhide__ = True

    vals = set()

    for i in iterable:
        if i in vals: return False

        vals.add(i)

    return True

def get_file_from_url(url):
    bn = os.path.basename(url)
    return os.path.join(config['outputDir'], bn)
