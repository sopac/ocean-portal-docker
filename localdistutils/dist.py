#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

from distutils.dist import Distribution

class PortalDist(Distribution):
    def __init__(self, attrs=None):
        self.web_files = None
        self.html_files = None

        Distribution.__init__(self, attrs)
