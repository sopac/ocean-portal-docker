#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Nick Summons <n.summons@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

"""
Simple script to update ERSST file format to avoid NCO utility bug.

This process converts the NetCDF SST data from Short (Scale Factor x Value
plus Offset) format to Float. This is necessary to avoid a bug in NCO utility
that handles this data type incorrectly and results in incorrect processed
values when calculating multi-month means.
"""

import os.path
import subprocess
from glob import glob

from ocean.config import get_server_config

def convert():
    config = get_server_config()

    input_dir = os.path.join(config.dataDir['ersst'], 'monthly')
    output_dir = os.path.join(config.dataDir['ersst'], 'monthly_processed')
    input_files = glob(os.path.join(input_dir, 'ersst.*.nc'))

    for input_file in input_files:
        filename = os.path.basename(input_file)
        output_filename = os.path.join(output_dir, filename)

        if not os.path.exists(output_filename) or \
           os.path.getmtime(input_file) > os.path.getmtime(output_filename):
            print '%s -> %s' % (input_file, output_filename)
            cmd = ['ncea', '--ovr', input_file, output_filename]
            proc = subprocess.call(cmd)

if __name__ == '__main__':
    print 'padger'
    convert()
