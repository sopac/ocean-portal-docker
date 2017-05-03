#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os
import subprocess

# options for pngcrush
PNGCRUSH = \
    'pngcrush -rem alla -rem text'

PNGCRUSH = PNGCRUSH.split()

def pngcrush(outfile, infile=None, delete_infile=None):
    if not infile:
        infile = outfile + '.tmp'
        os.rename(outfile, infile)
        if not delete_infile:
            delete_infile = True
    else:
        if not delete_infile:
            delete_infile = False

    with open(os.devnull, 'wb') as devnull:
        subprocess.check_call(PNGCRUSH + [infile, outfile],
                              stdout=devnull, stderr=devnull)
        if delete_infile:
            os.remove(infile)
