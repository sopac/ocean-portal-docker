#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os

def test_none_missing():
    """
    Confirm that no datasets are missing from __all__, this is required for
    the test below to be meaningful.
    """

    from ocean import datasets

    for d, dirs, files in os.walk(datasets.__path__[0]):
        print dirs
        break

    assert sorted(dirs) == sorted(datasets.__all__)

def test_import_all():
    """
    Test every dataset can be imported.
    """

    from ocean.datasets import *

def test_all_in_setup():
    """
    Test that all the datasets are present in setup.py.
    """

    import setup
    from ocean import datasets

    print setup.packages

    ds = [ d.rsplit('.', 1)[1] for d in setup.packages
                               if d.startswith(datasets.__name__ + '.') ]

    print ds

    assert sorted(ds) == sorted(datasets.__all__)
