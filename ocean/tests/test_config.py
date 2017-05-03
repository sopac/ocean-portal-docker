#
# (c) 2013 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import pytest

from ocean import config

def test_get_config():
    from ocean.config.serverConfig import tuscany

    cfg = config.get_server_config(hostname='tuscany')

    assert type(cfg) == tuscany

    assert cfg.hostname == cfg['hostname'] == 'tuscany.bom.gov.au'
    assert cfg.dataDir != {}

def test_unconfigured():

    with pytest.raises(config.UnconfiguredServer):
        config.get_server_config(hostname='non-existant-server')
