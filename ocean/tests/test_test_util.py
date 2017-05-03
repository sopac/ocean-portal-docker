#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import util

def test_unique():
    assert util.unique([1, 2, 3, 4])
    assert not util.unique([1, 1, 2, 3])
