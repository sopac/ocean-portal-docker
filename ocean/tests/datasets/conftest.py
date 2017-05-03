#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os
import shutil
import json
import datetime

import pytest

from ocean.tests import util

def pytest_generate_tests(__multicall__, metafunc):
    __multicall__.execute()

    if 'variable' in metafunc.fixturenames:
        # run the test for all possible variables
        variables = metafunc.module.Dataset.__variables__
        metafunc.parametrize('variable', variables)

    if 'period' in metafunc.fixturenames:
        # run the test for all possible periods
        periods = metafunc.module.Dataset.__periods__
        metafunc.parametrize('period', periods)

@pytest.mark.tryfirst
def pytest_runtest_makereport(__multicall__, item, call):
    rep = __multicall__.execute()

    try:
        report = item.funcargs['report']

        if rep.when == 'call' and rep.failed:
            report(status='failed')
    except KeyError:
        pass

    return rep

class JSONEncoder(json.JSONEncoder):
    """
    Extend JSONEncoder to serialize datetimes.
    """

    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)

class Report(object):
    """
    A class to generate a report.
    """

    def __init__(self):
        self._reports = []

        if 'WORKSPACE' in os.environ and \
           'BUILD_NUMBER' in os.environ:
            self._testdir = os.path.join(os.environ['WORKSPACE'],
                                         'test-reports',
                                         os.environ['BUILD_NUMBER'])
        else:
            # FIXME: make unique, write into the header
            self._testdir = '/tmp/test-report/'
            shutil.rmtree(self._testdir, True)

        os.makedirs(self._testdir)

    def report(self, nodeid, params=None, img=None, status='passed'):
        d = {
            'nodeid': nodeid,
            'status': status,
        }

        if params is not None:
            d['params'] = params

        if img is not None:
            file = util.get_file_from_url(img)

            assert os.path.exists(file)
            assert not os.path.exists(os.path.join(self._testdir, img))

            shutil.copy(file, self._testdir)
            d['img'] = img

        self._reports.append(d)

    def output(self):
        with open(os.path.join(self._testdir, 'report.json'), 'w') as f:
            json.dump(self._reports, f, cls=JSONEncoder, indent=2)

@pytest.fixture(scope='session')
def reportcls(request):

    r = Report()

    request.addfinalizer(lambda *args: r.output())

    return r

@pytest.fixture
def report(request, reportcls):

    return lambda *args, **kwargs: reportcls.report(request.node.nodeid,
                                                    *args, **kwargs)
