#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>
#          Sheng Guo <s.guo@bom.gov.au>

import os
import os.path
import sys
import re
import subprocess
import urlparse
import urllib
import hashlib
import shutil

from ocean import util
from ocean.config import get_server_config
from ocean.util.pngcrush import pngcrush

config = get_server_config()

if config['debug']:
    import cgitb
    cgitb.enable()

if 'PORTALPATH' in os.environ:
    os.environ['PATH'] = os.environ['PORTALPATH']

def main():
    queryMap = urlparse.parse_qs(os.environ["QUERY_STRING"])

    # update the query string
    if 'map' in queryMap:
        map = queryMap['map'][0]
        queryMap['map'] = util.get_resource('maps', map + '.map')

#        if map == 'raster':
#            queryMap['eastFileName'] = os.path.join(config['outputDir'], queryMap['eastmap'][0])
#            queryMap['westFileName'] = os.path.join(config['outputDir'], queryMap['westmap'][0])
#            rasters = queryMap['raster'][0].split(' ')
#
#            MAP_EAST_PATTERN = re.compile('east.png$')
#            MAP_WEST_PATTERN = re.compile('west.png$')
#
#            for file in rasters:
#                filename = os.path.basename(file)
#
#                if MAP_EAST_PATTERN.search(filename):
#                    queryMap['eastFileName'] = os.path.join(config['outputDir'],
#                                                            filename)
#                elif MAP_WEST_PATTERN.search(filename):
#                    queryMap['westFileName'] = os.path.join(config['outputDir'],
#                                                            filename)
        if map in ['mean', 'mean_sub', 'anom', 'dec', 'trend', 'hs', 'chlo', 'coral_daily', 'coral_outlook',\
                   'wav', 'wnd', 'grey', 'poamasla', 'current', 'mur', 'contour', 'normal', 'salt', 'uv', 'front',\
                   'height']:
            queryMap['base'] = config['outputDir'] + os.path.basename(os.path.splitext(queryMap['mapimg'][0])[0])
    queryString = urllib.urlencode(queryMap, True)
    m = hashlib.sha256()
    m.update(queryString)

    hash = m.hexdigest()
    etag = '"%s"' % hash

    filename = os.path.join(config['outputDir'], 'maptiles', '%s.png' % hash)

    # determine whether or not we need to call into mapserver
    try:
        mapimg = os.path.join(config['outputDir'] + os.path.basename(queryMap['mapimg'][0]))
        cache_mtime = os.path.getmtime(filename)
        call_mapserver = cache_mtime < os.path.getmtime(mapimg)
               # cache_mtime < os.path.getmtime(queryMap['mapimg'][0])
    except os.error:
        call_mapserver = True
    except KeyError:
        call_mapserver = not os.path.exists(filename)

    # call mapserver if required
    if call_mapserver:
        with os.tmpfile() as tmpfile:
            os.environ['QUERY_STRING'] = queryString
            subprocess.call(config['mapservPath'], stdout=tmpfile)
            # remove the first two lines from the tmpfile to make it a png
            tmpfile.seek(0)
            content_type = tmpfile.readline().strip().split(' ', 2)[1]
            # check to see if mapserver generated an error
            if content_type != 'image/png':
                print 'Status: 500 Internal Server Error'
                print 'Content-Type: %s' % content_type
                print 'X-Portal-Version: %s' % util.__version__
                print
                print tmpfile.read()
                return

            tmpfile.readline()

            with open(filename, 'wb') as cachefile:
                # copy it to the output file
                shutil.copyfileobj(tmpfile, cachefile)

        pngcrush(filename)

    else:
        try:
            if os.environ['HTTP_IF_NONE_MATCH'] == etag:
                print 'Status: 304 Not Modified'
                print 'X-Portal-Version: %s' % util.__version__
                print
                return
        except KeyError:
            pass

    # play the cached file to the web server
    with open(filename, 'rb') as cachefile:
        print 'Status: 200 Ok'
        print 'Content-Type: image/png'
        print 'ETag: %s' % etag
        print 'Cache-Control: max-age=3600' # FIXME: value?
        print 'X-Tile-Cached:', 'no' if call_mapserver else 'yes'
        print 'X-Portal-Version: %s' % util.__version__
        print

        shutil.copyfileobj(cachefile, sys.stdout)

if __name__ == '__main__':
    main()
