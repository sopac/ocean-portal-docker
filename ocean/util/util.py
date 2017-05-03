#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os
import os.path
import datetime

import ocean

def import_dataset(dataset):
    module = __import__('ocean.datasets.%s' % (dataset),
                        fromlist=[''])

    try:
        ds = module.Dataset
    except AttributeError as e:
        raise ImportError(e)

    return ds

def get_resource(*args):
    """
    Return the path to a resource.
    """

    return os.path.join(ocean.__path__[0], 'resource', *args)

def check_files_exist(basename, subnames):
    """
    Returns: True if the list of files basename+subnames[0, 1, 2, etc..] exist.
    """

    return reduce(lambda a, p: a and os.path.exists(basename + p),
        subnames, True)

def build_response_object(fields, basename, subnames):
    return dict([ (k, basename + v) for (k, v) in zip(fields, subnames) ])

def touch_files(basename, subnames):
    for n in subnames:
        try:
            os.utime(basename + n, None)
        except OSError:
            pass # eat it

def format_old_date(d):
    """
    date.strftime() doesn't deal with dates before 1900, which doesn't suit
    us for ERSST.

    Returns: a formatted date string
    """

    h = datetime.date(2000, d.month, d.day)
    return '%s %s' % (h.strftime('%B'), d.year)
