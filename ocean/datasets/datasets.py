#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import cgi
import datetime

from ocean.config import regionConfig
from ocean.core import ReportableException

class MissingParameter(ReportableException):
    pass

class ValidationError(ReportableException):
    pass

class Dataset(object):

    # these are the possible paramaters that can be passed to a dataset
    # and their types
    __form_params__ = {
        'dataset': str,
        'variable': str,
        'plot': str,
        'date': datetime.date,
        'period': str,
        'area': str,
        'step': str,
    }

    # these parameters are required, failure to include them is an exception
    __required_params__ = [
        'dataset',
        'variable',
        'plot',
        'period',
    ]

    __periods__ = [
    ]

    __variables__ = [
    ]

    __plots__ = [
    ]

    @classmethod
    def parse(self, validate=True):
        form = cgi.FieldStorage()

        output = {}

        for k, t in self.__form_params__.items():
            if k not in form:
                continue

            v = form[k].value

            # coerce the form values into the right types
            if hasattr(self, 'parse_%s' % k):
                v = getattr(self, 'parse_%s' % k)(v)

                if not isinstance(v, t):
                    raise TypeError("Form parameter '%s' is of type %s, expected %s" %
                                    (k, type(v), t))
            else:
                v = t(v)

            # run validation
            # FIXME: should this be done afterwards with the entire param set?
            if validate and hasattr(self, 'validate_%s' % k):
                try:
                    getattr(self, 'validate_%s' % k)(v)
                except AssertionError, e:
                    raise ValidationError(e)

            output[k] = v

        # check for required 
        if validate:
            for k in self.__required_params__:
                if k not in output:
                    raise MissingParameter("Expected parameter '%s'" % k)

        return output

    @classmethod
    def parse_date(self, p):
        if len(p) == 8:
            day = int(p[6:8])
        elif len(p) == 6:
            day = 1
        else:
            raise TypeError("Length of date must be 6 or 8, not %i" % len(p))

        return datetime.date(int(p[0:4]), int(p[4:6]), day)

    @classmethod
    def validate_variable(self, p):
        if not p in self.__variables__:
            raise ValidationError("Unknown variable '%s'" % p)

    @classmethod
    def validate_plot(self, p):
        if not p in self.__plots__:
            raise ValidationError("Unknown plot type '%s'" % p)

    @classmethod
    def validate_period(self, p):
        if not p in self.__periods__:
            raise ValidationError("Unknown period '%s'" % p)

    @classmethod
    def validate_area(self, p):
        if p not in regionConfig.regions:
            raise ValidationError("Unknown area '%s'" % p)

    def process(self, params):
        raise NotImplemented
