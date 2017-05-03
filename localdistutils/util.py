#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import subprocess
from StringIO import StringIO

def get_version():
    proc = subprocess.Popen(['git', 'describe', '--dirty=-modified'],
                            stdout=subprocess.PIPE)
    (stdout, _) = proc.communicate()
    proc.wait()

    return stdout.strip()
