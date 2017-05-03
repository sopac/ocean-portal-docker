#
# (c) 2013 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import csv
import datetime
import os.path

import numpy as np

from ocean.config import get_server_config

config = get_server_config()

class TideGauge(np.recarray):
    """
    Class for reading NTC monthly tide gauge analysis reports and loading them
    into a numpy array.
    """

    COLUMNS = [
        ('date', datetime.date),
        ('mth', int),
        ('year', int),
        ('gaps', int),
        ('good', int),
        ('minimum', float),
        ('maximum', float),
        ('mean_', float),
        ('stdev', float),
    ]

    def __new__(cls, productId):
        filename = os.path.join(config['dataDir']['sealevel'],
                                'gauges-new',
                                productId + 'SLD.txt')

        with open(filename) as f:

            # skip the header
            header = False

            for line in f:
                if not header and line.strip() != '':
                    header = True
                elif header and line.strip() == '':
                    break

            reader = csv.reader(f, delimiter=' ', skipinitialspace=True)

            # load the headers
            headers = reader.next()
            # 'St Dev' has a space in it :-/
            # FIXME, set this as titles
            headers.append(' '.join(reversed([headers.pop(), headers.pop()])))
            headers.insert(0, "Date")

            nheaders = len(headers)

            assert len(cls.COLUMNS) == nheaders

            # read in the data using a generator
            # the generator will add a Python date object, and stop parsing
            # once the first row with the wrong number of columns is reached
            def generate():
                for row in reader:
                    if len(row) != nheaders - 1:
                        if row[0] == 'Totals':
                            raise StopIteration
                        else:
                            # pad missing values with NaNs
                            row += [np.nan] * (nheaders - len(row) - 1)

                    month, year = row[0:2]
                    date = datetime.date(day=1,
                                         month=int(month),
                                         year=int(year))

                    yield tuple([date] + row)

            # load the data
            data = list(generate())

            r = np.array(data, dtype=cls.COLUMNS).view(cls)
            r.headers = headers

            return r
