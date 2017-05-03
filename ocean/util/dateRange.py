#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import datetime
from warnings import warn
from dateutil.relativedelta import *

weekDelta = [relativedelta(weekday=MO),
             relativedelta(weekday=TU),
             relativedelta(weekday=WE),
             relativedelta(weekday=TH),
             relativedelta(weekday=FR),
             relativedelta(weekday=SA),
             relativedelta(weekday=SU)
             ]

def compatible_datetime(func):
    """
    Decorator to handle old-style arguments do this function.
    """

    def inner(date, *args):
        if not isinstance(date, datetime.date):
            # for compatibility with code that passes dates as strings
            warn("Passing strings for dates is deprecated", DeprecationWarning)

            year = int(date[0:4])
            month = int(date[4:6])
            day = int(date[6:8])

            date = datetime.date(year, month, day)

        return func(date, *args)

    return inner

@compatible_datetime
def getMonths(date, monthRange):
    """
    Get the months using the input date as the last month and count back in
    time.
    """

    months = [ date + relativedelta(months=-delta)
               for delta in range(monthRange) ]
    months.reverse()

    return months

@compatible_datetime
def getWeekDays(date):
    """
    Get the week days given a date. The date can be any day in a week.
    """

    if (date.weekday() != 0):
        date = date - datetime.timedelta(date.weekday())

    return [ date + delta for delta in weekDelta ]

@compatible_datetime
def weeks_between(d1, d2):
    """
    Get the total number of weeks between two dates. The date can be any day in a week.
    """
    monday1 = (d1 - datetime.timedelta(days=d1.weekday()))
    monday2 = (d2 - datetime.timedelta(days=d2.weekday()))
    return (monday2 - monday1).days / 7