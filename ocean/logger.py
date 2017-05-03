#
# (c) 2013 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import csv
import os
import os.path
import sys
from datetime import datetime
from functools import wraps
from warnings import warn

from ocean import config

cfg = config.get_server_config()

class _Logger(object):

    def __init__(self, path=None, filename=None, file=None):
        self._timers = {}

        if file is None:
            if path is None:
                path = os.path.join(cfg['outputDir'], 'logs')

            if filename is None:
                filename = '%s.csv' % os.getpid()

            try:
                os.makedirs(path)
            except OSError:
                pass

            self.logfile = open(os.path.join(path, filename), 'a')
        else:
            self.logfile = file

        self.writer = csv.writer(self.logfile)

        print >> self.logfile, "# %s instance started %s" % (
            sys.argv[0], datetime.now().strftime('%c'))

    def __del__(self):
        self.logfile.close()

    def log(self, *args):
        time = datetime.now()
        self.writer.writerow([time.isoformat()] + list(args))
        self.logfile.flush()

    def start_timer(self, timer_name):
        if timer_name in self._timers:
            warn("Timer %s already started" % timer_name, RuntimeWarning)
            return

        self._timers[timer_name] = datetime.now()

    def stop_timer(self, timer_name, log=True):
        try:
            time = datetime.now()
            delta = time - self._timers[timer_name]
            elapsed = delta.seconds + delta.microseconds / 1e6

            del self._timers[timer_name]

            if log:
                self.log(timer_name, '', elapsed)

            return elapsed
        except KeyError:
            warn("Timer %s is not running" % timer_name, RuntimeWarning)

            return None

    def time_and_log(self, arg1):
        """
        Decorator to time the execution of a function/method and log it.
        """

        if not callable(arg1):
            name = arg1
        else:
            name = None

        def outer(func):

            if name is None:
                timer_name = func.__name__
            else:
                timer_name = name

            @wraps(func)
            def inner(*args, **kwargs):
                __tracebackhide__ = True

                self.start_timer(timer_name)
                r = func(*args, **kwargs)
                self.stop_timer(timer_name)

                return r

            return inner

        if callable(arg1):
            return outer(arg1)
        else:
            return outer

# singleton logger
_logger = _Logger()

# global methods
log = _logger.log
start_timer = _logger.start_timer
stop_timer = _logger.stop_timer
time_and_log = _logger.time_and_log
