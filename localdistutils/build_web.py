#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os.path
import subprocess
import re

from distutils.core import Command
from distutils.util import convert_path

from distutils import log

from jsmin import JavascriptMinify
from cssmin import cssmin
import util

class build_web(Command):

    description = "Build (minify) web resources"

    user_options = [
        ('build-dir=', 'd', "directory to \"build\" to"),
        ('force', 'f', "forcibly build everything (ignore file timestamps"),
        ('compress', None, "Compress (minify) web resources"),
        ]

    boolean_options = [ 'force', 'compress' ]

    def initialize_options(self):
        self.build_dir = None
        self.build_base = None
        self.force = None
        self.compress = None
        self.web_files = []

        self.outfiles = []

    def finalize_options(self):
        self.set_undefined_options('build',
            ('build_base', 'build_base'),
            ('compress', 'compress'),
            ('force', 'force'))

        if self.build_dir is None:
            self.build_dir = os.path.join(self.build_base, 'web')

        self.web_files = self.distribution.web_files[1]
        (_, self.html_files, self.html_subst) = self.distribution.html_files

        self.version = util.get_version()

        if not self.compress:
            self.compress = False

    def get_source_files(self):
        return self.web_files + self.html_files

    def run(self):
        self.mkpath(self.build_dir)

        outfiles = []
        updated_files = []

        # consider replacing this with a better utility
        jsm = JavascriptMinify()

        for f in self.web_files:
            inf = convert_path(f)
            outf = os.path.join(self.build_dir, f)

            self.mkpath(os.path.dirname(outf))

            if self.compress:
                log.info("minifying %s -> %s" % (f, outf))

                input = open(inf, 'r')
                output = open(outf, 'wb')

                if f.endswith('.js'):
                    # eat the first line (JSLint directive)
                    input.readline()

                # copy 5 lines of the header
                for l in range(6):
                    output.write(input.readline())

                if f.endswith('.js'):
                    jsm.minify(input, output)
                elif f.endswith('.css'):
                    output.write(cssmin(input.read()))

                input.close()
                output.close()
            else:
                self.copy_file(inf, outf)

            self.outfiles.append(outf)

        # build a regular expression to substitute the HTML files
        regex = ';'.join([ 's/{{%s}}/%s/' % (
            re.escape(k), re.escape(v[self.compress]))
            for k, v in self.html_subst.iteritems() ])
        regex += ';s/{{VERSION}}/%s/' % (re.escape(self.version))

        for f in self.html_files:
            inf = convert_path(f)
            outf = os.path.join(self.build_dir, os.path.basename(f))

            log.info("substituting %s -> %s" % (f, outf))
            output = open(outf, 'wb')

            # use sed, because I like sed
            subprocess.check_call(['sed', regex, inf], stdout=output)
            output.close()

            self.outfiles.append(outf)
