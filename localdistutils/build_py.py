#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os

from distutils.command.build_py import build_py as real_build_py
from distutils import log

import util

ver = util.get_version()

LOOK_BACK = 100 # chars

def try_and_seek(f, offset):
    try:
        f.seek(offset, os.SEEK_END)
    except IOError:
        # file too short
        pass

class build_py(real_build_py):

    def build_module(self, module, module_file, package):
        real_build_py.build_module(self, module, module_file, package)

        # append version to every module
        package = package.split('.')
        outfile = self.get_module_outfile(self.build_lib, package, module)

        with open(outfile, 'r+U') as module:
            verstr = "__version__ = '%s'" % (ver)

            try_and_seek(module, -LOOK_BACK)

            # do we have a version string?
            line = module.read()
            idx = line.rfind('\n__version__')

            if idx != -1:
                # is it the right version string?
                idx = -len(line) + idx

                try_and_seek(module, idx)
                line = module.read().strip()

                if line == verstr:
                    # all good in the hood
                    return
                else:
                    try_and_seek(module, idx)
                    module.truncate()
            else:
                # no version string found
                pass

            # write the version string
            log.info('writing version: %s' % outfile)
            try_and_seek(module, 0)
            print >> module
            print >> module, verstr
