#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Author: Sheng Guo <s.guo@bom.gov.au>
#         Danielle Madeley <d.madeley@bom.gov.au>

"""
Store the server specific configurations

Don't import config directly, use ocean.config.get_server_config()
"""

from ocean.config import BaseConfig

class default(BaseConfig):
    """
    Default server config. Inherit this class to set per-server config.
    """

    # path on web server
    baseURL = '/portal/'

    # relative path to rasters
    rasterURL = 'comp/raster/'

    # path on disk to output rasters/caches
    outputDir = '/opt/data/comp/raster/'

    # relative path to caches (relative to rasterURL) (obsolete?)
    cacheDir = {
        'reynolds': 'cache/reynolds/',
        'ersst': 'cache/ersst/',
    }

    dataDir = {}

    mapservPath = '/usr/lib/cgi-bin/mapserv'
    debug = True
    profile = False

class localhost(default):
    debug = True
    mapservPath = '/usr/lib/cgi-bin/mapserv'
    dataDir = {
        'bran': '/opt/data/blue_link/data/',
        'ersst': '/opt/data/sst/ersst/data/',
        'reynolds': '/opt/data/sst/reynolds/',
        'sealevel': '/opt/data/sea_level/',
        'msla': '/opt/data/sea_level/',
        'ww3': '/opt/data/wavewatch3/',
        'coral':'/opt/data/sst/coral/',
        'poamasla':'/opt/data/poama/',
        'poamassta':'/opt/data/poama/',
        'oceanmaps':'/opt/data/oceanmaps/',
        'chloro':'/opt/data/chloro/',
        'currents':'/opt/data/currents/',
        'ww3forecast':'/opt/data/wavewatch3/forecast/',
        'mur':'/opt/data/sst/mur/'
    }



class oceanportal(default):
    debug = True
    mapservPath = '/usr/lib/cgi-bin/mapserv'
    dataDir = {
        'bran': '/opt/data/blue_link/data/BRAN3p5/',
        'ersst': '/opt/data/sst/ersst/data/',
        'reynolds': '/opt/data/sst/reynolds/',
        'sealevel': '/opt/data/sea_level/',
        'msla': '/opt/data/sea_level/',
        'ww3': '/opt/data/wavewatch3/',
        'coral':'/opt/data/sst/coral/',
        'coral_ol':'/opt/data/sst/coral/',
        'poamasla':'/opt/data/poama/',
        'poamassta':'/opt/data/poama/',
        'oceanmaps':'/opt/data/oceanmaps/',
        'chloro':'/opt/data/chloro/',
        'currents':'/opt/data/currents/',
        'ww3forecast':'/opt/data/wavewatch3/forecast/',
        'mur':'/opt/data/sst/mur/'
    }

class tunceli(default):
    debug = True

    # shared data directories from ITB (mounted rw)
    dataDir = {
        'bran': '/www4/data/cosppac/bran/',
        'ersst': '/www4/data/cosppac/ersst/',
        'reynolds': '/www4/data/cosppac/reynolds/',
        'sealevel': '/www4/data/cosppac/sea_level/',
        'msla': '/www4/data/cosppac/sea_level/',
        'ww3': '/www4/data/cosppac/wavewatch3/',
        'coral':'/www4/data/cosppac/coral/',
        'coral_ol':'/www4/data/cosppac/coral/',
        'poamasla':'/www4/data/cosppac/poama/',
        'poamassta':'/www4/data/cosppac/poama/',
        'oceanmaps':'/www4/data/cosppac/oceanmaps/',
        'chloro':'/www4/data/cosppac/chloro/',
        'currents':'/www4/data/cosppac/currents/',
        'ww3forecast':'/www4/data/cosppac/wavewatch3/forecast/',
	'mur':'/www4/data/cosppac/mur/'
    }

class www4(default):
    debug = True
    baseURL = '/cosppac/apps/portal/'
    outputDir = '/web/cosppac/raster/'

    dataDir = {
        'bran': '/web/data/cosppac/bran/',
        'ersst': '/web/data/cosppac/ersst/',
        'reynolds': '/web/data/cosppac/reynolds/',
        'sealevel': '/web/data/cosppac/sea_level/',
        'msla': '/web/data/cosppac/sea_level/',
        'ww3': '/web/data/cosppac/wavewatch3/',
        'coral': '/web/data/cosppac/coral/',
        'coral_ol': '/web/data/cosppac/coral/',
        'poamasla':'/web/data/cosppac/poama/',
        'poamassta':'/web/data/cosppac/poama/',
        'oceanmaps': '/web/data/cosppac/oceanmaps/',
        'chloro':'/web/data/cosppac/chloro/',
        'currents':'/web/data/cosppac/currents/',
        'ww3forecast':'/web/data/cosppac/wavewatch3/forecast/',
	'mur':'/web/data/cosppac/mur'
    }

class hoapp2(www4):
    debug = False

__version__ = '1.0.1-1-gc7181e8'
