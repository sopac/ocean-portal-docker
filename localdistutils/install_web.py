#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os.path

from distutils.core import Command
from distutils import log
from distutils.util import change_root

class install_web(Command):

    description = "Install minified web resources"

    user_options = [
        ('install-dir=', 'd', "directory to install resources to"),
        ('root=', None, "install everything relative to this alternate root directory"),
        ('build-dir=', 'b', "build directory (where to install from"),
        ('force', 'f', "force installation (overwrite existing files)"),
        ('skip-build', None, "skip the build steps"),
        ]

    boolean_options = ['force', 'skip-build']

    def initialize_options(self):
        self.install_dir = None
        self.build_dir = None
        self.root = None
        self.force = None
        self.skip_build = None
        self.outfiles = None

    def finalize_options(self):
        self.set_undefined_options('build_web', ('build_dir', 'build_dir'))
        self.set_undefined_options('install_data', ('install_dir', 'install_dir'))
        self.set_undefined_options('install',
                                   ('root', 'root'),
                                   ('force', 'force'),
                                   ('skip_build', 'skip_build'),
                                  )

    def run(self):
        if not self.skip_build:
            self.run_command('build_web')

        dir = os.path.join(self.install_dir, self.distribution.web_files[0])

        # FIXME: dodgy workaround
        if self.root and not dir.startswith(self.root):
            dir = change_root(self.root, dir)

        self.outfiles = self.copy_tree(self.build_dir, dir)

    def get_inputs(self):
        return self.distribution.web_files[1] or []

    def get_outputs(self):
        return self.outfiles or []
