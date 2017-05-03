#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os
import urllib
import datetime

import pytest

from ocean.datasets import Dataset, MissingParameter, ValidationError

class MyDataset(Dataset):

    __form_params__ = {
        'odd': int,
    }
    __form_params__.update(Dataset.__form_params__)

    __variables__ = Dataset.__variables__ + [
        'snake',
    ]

    __periods__ = Dataset.__periods__ + [
        'monthly',
    ]

    __required_params__ = [
        'dataset',
        'variable',
    ]

    @classmethod
    def validate_odd(self, p):
        assert p % 2 == 1

def test_parse_basic():
    """
    This is a basic test of the Dataset parameter parsing.
    """

    qs = urllib.urlencode({
        'dataset': 'badger',
        'variable': 'snake',
    })

    os.environ['QUERY_STRING'] = qs

    params = MyDataset.parse()

    assert params == { 'dataset': 'badger',
                       'variable': 'snake' }

def test_parse_missing_param():
    """
    Test the MissingParameter exception.
    """

    qs = urllib.urlencode({
        'dataset': 'badger',
    })

    os.environ['QUERY_STRING'] = qs

    with pytest.raises(MissingParameter):
        MyDataset.parse()

def test_parse_invalid_var():
    """
    Test the MissingParameter exception.
    """

    qs = urllib.urlencode({
        'dataset': 'badger',
        'variable': 'snake',
    })

    os.environ['QUERY_STRING'] = qs

    with pytest.raises(ValidationError):
        Dataset.parse() # uses base dataset

def test_parse_unknown_param():
    """
    Test unknown params.
    """

    qs = urllib.urlencode({
        'dataset': 'badger',
        'variable': 'snake',
        'unknownparam': 'unknown',
    })

    os.environ['QUERY_STRING'] = qs

    params = MyDataset.parse()

    assert params == { 'dataset': 'badger',
                       'variable': 'snake' }

def test_parse_date():
    """
    Test parsing of dates of form yyyymmdd.
    """

    qs = urllib.urlencode({
        'dataset': 'badger',
        'variable': 'snake',
        'date': '20111231',
    })

    os.environ['QUERY_STRING'] = qs

    params = MyDataset.parse()

    assert params['date'] == datetime.date(2011, 12, 31)

def test_parse_date_month():
    """
    Test parsing of dates of form yyyymm.
    """

    qs = urllib.urlencode({
        'dataset': 'badger',
        'variable': 'snake',
        'date': '201112',
    })

    os.environ['QUERY_STRING'] = qs

    params = MyDataset.parse()

    assert params['date'] == datetime.date(2011, 12, 1)

def test_parse_date_bad():
    qs = urllib.urlencode({
        'dataset': 'badger',
        'variable': 'snake',
        'date': '2011121', # bad value
    })

    os.environ['QUERY_STRING'] = qs

    with pytest.raises(TypeError):
        MyDataset.parse()

def test_parse_validate_area():
    qs = urllib.urlencode({
        'dataset': 'badger',
        'variable': 'snake',
        'area': 'pac',
    })

    os.environ['QUERY_STRING'] = qs

    MyDataset.parse()

def test_parse_validate_area_bad():
    qs = urllib.urlencode({
        'dataset': 'badger',
        'variable': 'snake',
        'area': 'very_bad_area', # bad value
    })

    os.environ['QUERY_STRING'] = qs

    with pytest.raises(ValidationError):
        MyDataset.parse()

def test_parse_validate_period_monthly():
    qs = urllib.urlencode({
        'dataset': 'badger',
        'variable': 'snake',
        'period': 'monthly', # bad value
    })

    os.environ['QUERY_STRING'] = qs

    MyDataset.parse()

def test_parse_validate_period_bad():
    qs = urllib.urlencode({
        'dataset': 'badger',
        'variable': 'snake',
        'period': 'monthly', # bad value
    })

    os.environ['QUERY_STRING'] = qs

    with pytest.raises(ValidationError):
        Dataset.parse() # use base dataset

def test_custom_param():
    qs = urllib.urlencode({
        'dataset': 'badger',
        'variable': 'snake',
        'odd': 2, # bad value
    })

    os.environ['QUERY_STRING'] = qs

    with pytest.raises(ValidationError):
        MyDataset.parse() # use base dataset
