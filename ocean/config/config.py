#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import socket

from ocean.core import ReportableException

class UnconfiguredServer(ReportableException):
    def __init__(self, hostname):
        ReportableException.__init__(self,
            "The server %s is not configured" % hostname)

class BaseConfig(object):
    """
    Code for config classes. Do not inherit directly, instead inherit
    ocean.config.default.
    """

    def __getitem__(self, k):
        return getattr(self, k)

    @property
    def hostname(self):
        return socket.gethostname()

def get_server_config(hostname=None):
    if not hostname:
        hostname = socket.gethostname().split('.', 2)[0]

    import serverConfig as rc

    try:
        return getattr(rc, hostname)()
    except AttributeError:
        raise UnconfiguredServer(hostname)
