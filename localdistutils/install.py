#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

from distutils.command.install import install as real_install

class install(real_install):

    sub_commands = real_install.sub_commands + [
        ('install_web', lambda *args: True),
    ]
