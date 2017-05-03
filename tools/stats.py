#!/usr/bin/env python

import os.path
import sys
import pstats
import glob

class Stats(pstats.Stats):

    def print_stats_short(self, *amount):
        width, list = self.get_print_list(amount)
        if list:
            self.print_title()
            for func in list:
                self.print_line(func)

            print >> self.stream
            print >> self.stream

        return self

func_std_string_real = pstats.func_std_string

def func_std_string((file, line, func)):
    if file == '~' and line == 0:
        pass
    else:
        f = file.split('/')
        try:
            f = f[f.index('site-packages') + 1:]
            file = os.path.join(*f)
        except ValueError:
            file = '[%s]' % f[-1]

    return func_std_string_real((file, line, func))

pstats.func_std_string = func_std_string

def __main__():
    files = glob.glob('/tmp/portal.profile.*')

    if not files:
        print >> sys.stderr, "No profiles"
        return -1

    stats = Stats(files[0])
    stats.add(*files[1:])

    # stats.strip_dirs()
    stats.sort_stats('time').print_stats(*sys.argv[1:] + [15])
    stats.sort_stats('cumulative').print_stats_short(*sys.argv[1:] + [15])

if __name__ == '__main__':
    __main__()
