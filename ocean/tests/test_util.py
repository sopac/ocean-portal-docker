#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import datetime

import pytest

import ocean
from ocean import util

def test_get_resource():
    p = util.get_resource('maps', 'raster.map')
    assert p.startswith(ocean.__path__[0])
    assert p.endswith('maps/raster.map')

def test_build_response_object():
    o = util.build_response_object(
        ['a', 'b', 'c'],
        'canoe',
        ['.png', '.jpg', '.txt'])

    assert o == {
        'a': 'canoe.png',
        'b': 'canoe.jpg',
        'c': 'canoe.txt',
    }

def test_format_old_date():
    d = datetime.date(1900, 1, 1)
    ds = util.format_old_date(d)

    assert ds == 'January 1900'

    d = datetime.date(2000, 3, 1)
    ds = util.format_old_date(d)

    assert ds == 'March 2000'

    d = datetime.date(1850, 5, 1)
    ds = util.format_old_date(d)

    assert ds == 'May 1850'

def test_funcregister_good():
    class Test(object):
        apply_to = util.Parameterise()

        @apply_to(variable='mean')
        def get_filename(self, params={}):
            return 'canoe'

        @apply_to(variable='anom')
        def get_filename(self, params={}):
            return 'yacht'

    t = Test()

    assert t.get_filename(params={ 'variable': 'mean'}) == 'canoe'
    assert t.get_filename(params={ 'variable': 'anom'}) == 'yacht'

    with pytest.raises(AttributeError) as e:
        t.get_filename(params={ 'variable': 'dec' })

    assert e.value.message.startswith('No function')

def test_funcregister_ambiguous():
    class Test(object):
        apply_to = util.Parameterise()

        @apply_to(variable='mean')
        def get_filename(self, params={}):
            return 'canoe'

        @apply_to(period='monthly')
        def get_filename(self, params={}):
            return 'yacht'

    t = Test()

    with pytest.raises(AttributeError) as e:
        t.get_filename(params={ 'variable': 'mean', 'period': 'monthly' })

    assert e.value.message.startswith('Ambiguous')

def test_funcregister_good_multi():
    class Test(object):
        apply_to = util.Parameterise()

        @apply_to(variable='mean', period='monthly')
        def get_filename(self, params={}):
            return 'Monthly Mean'

        @apply_to(variable='anom', period='monthly')
        def get_filename(self, params={}):
            return 'Monthly Anom'

    t = Test()
    t.badger = 1

    assert t.get_filename(params={ 'variable': 'mean', 'period': 'monthly' }) \
        == 'Monthly Mean'
    assert t.get_filename(params={ 'variable': 'anom', 'period': 'monthly' }) \
        == 'Monthly Anom'

    with pytest.raises(AttributeError) as e:
        t.get_filename(params={ 'variable': 'dec', 'period': 'monthly' })

    assert e.value.message.startswith('No function')

def test_funcregister_tight_binding_good():
    class Test(object):
        apply_to = util.Parameterise()

        @apply_to()
        def get_title(self, params={}):
            return 'Monthly Average'

        @apply_to(variable='anom')
        def get_title(self, params={}):
            return 'Monthly Anom'

    t = Test()

    assert t.get_title(params=dict(variable='mean')) == 'Monthly Average'
    assert t.get_title(params=dict(variable='anom')) == 'Monthly Anom'
    assert t.get_title(params={}) == 'Monthly Average'

def test_funcregister_tight_binding_ambiguous():
    class Test(object):
        apply_to = util.Parameterise()

        @apply_to(period='monthly')
        def get_title(self, params={}):
            return 'Monthly Average'

        @apply_to(variable='anom')
        def get_title(self, params={}):
            return 'Monthly Anom'

    t = Test()

    with pytest.raises(AttributeError) as e:
        t.get_title(params=dict(variable='anom', period='monthly'))

    assert e.value.message.startswith('Ambiguous')

def test_funcregister_ignore():
    class Test(object):
        apply_to = util.Parameterise()

        @apply_to()
        def get_path(self, params={}):
            return '/usual/path'

        @apply_to(variable='dec')
        def get_path(self, params={}):
            return '/deciles/path'

    class TestSubClass(Test):
        apply_to = util.Parameterise(Test)

        @apply_to(period='monthly')
        def get_path(self, params={}):
            return '/original/data/path'

        @apply_to(period='monthly', variable='dec')
        def get_path(self, params={}):
            return self.get_path(params=params, _ignore=['period'])

    t = TestSubClass()

    assert t.get_path(params=dict(variable='anom',
                                  period='monthly')) == '/original/data/path'
    assert t.get_path(params=dict(variable='anom',
                                  period='3monthly')) == '/usual/path'
    assert t.get_path(params=dict(variable='dec',
                                  period='monthly')) == '/deciles/path'
    assert t.get_path(params=dict(variable='dec',
                                  period='3monthly')) == '/deciles/path'

def test_funcregister_subclass():
    class BaseTest(object):
        apply_to = util.Parameterise()

        @apply_to()
        def get_a(self, params={}):
            return 'a'

    class Lowercase(BaseTest):
        apply_to = util.Parameterise(BaseTest)

        @apply_to()
        def get_b(self, params={}):
            return 'b'

    class Uppercase(BaseTest):
        apply_to = util.Parameterise(BaseTest)

        @apply_to()
        def get_b(self, params={}):
            return 'B'

    t = Lowercase()
    T = Uppercase()

    assert t.get_a(params={}) == 'a'
    assert t.get_b(params={}) == 'b'
    assert T.get_a(params={}) == 'a' # yes, lowercase
    assert T.get_b(params={}) == 'B'

def test_daterange_get_months_from_datetime():
    d = datetime.datetime(year=2000, month=3, day=1)

    jan, feb, mar = util.dateRange.getMonths(d, 3)

    assert jan.year == 2000 and jan.month == 1
    assert feb.year == 2000 and feb.month == 2
    assert mar.year == 2000 and mar.month == 3

def test_daterange_get_months_from_date():
    d = datetime.date(year=2000, month=1, day=1)

    oct, nov, dec, jan = util.dateRange.getMonths(d, 4)

    assert oct.year == 1999 and oct.month == 10
    assert nov.year == 1999 and nov.month == 11
    assert dec.year == 1999 and dec.month == 12
    assert jan.year == 2000 and jan.month == 1

def test_daterange_get_months_from_string(recwarn):
    oct, nov = util.dateRange.getMonths('20081116', 2)

    assert oct.year == 2008 and oct.month == 10
    assert nov.year == 2008 and nov.month == 11

    w = recwarn.pop()

    assert issubclass(w.category, DeprecationWarning)

def test_daterange_get_weekdays():

    WEEK_7 = range(11, 18) # week 7 of 2013

    for day in WEEK_7:
        d = datetime.date(year=2013, month=2, day=day)

        assert util.dateRange.getWeekDays(d) == [
            datetime.date(year=2013, month=2, day=i)
            for i in WEEK_7
        ]

def test_daterange_get_weekdays_across_year():

    d = datetime.date(year=2013, month=1, day=1)

    assert util.dateRange.getWeekDays(d) == [
        datetime.date(year=2012, month=12, day=31),
        datetime.date(year=2013, month=1, day=1),
        datetime.date(year=2013, month=1, day=2),
        datetime.date(year=2013, month=1, day=3),
        datetime.date(year=2013, month=1, day=4),
        datetime.date(year=2013, month=1, day=5),
        datetime.date(year=2013, month=1, day=6),
    ]
