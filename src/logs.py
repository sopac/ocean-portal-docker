#!/usr/bin/env python

import cgi
import cgitb
import os
import os.path
import sys
from glob import glob

from ocean.config import get_server_config

config = get_server_config()

if config['debug']:
    import cgitb
    cgitb.enable()

if 'PORTALPATH' in os.environ:
    os.environ['PATH'] = os.environ['PORTALPATH']

def output_logs():
    logs = glob(os.path.join(config['outputDir'], 'logs', '*'))

    for l in logs:
        with open(l) as log:
            print "# logs from %s" % (os.path.basename(l))
            for line in log:
                sys.stdout.write(line)

def main():
    print 'Content-Type:', 'text/csv;', 'charset=utf-8'
    print 'Content-Disposition:', 'attachment;', 'filename="logs.csv"'
    print
    output_logs()

if __name__ == '__main__':
    main()
