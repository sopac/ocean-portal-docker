#!/usr/bin/python
#
# (c) 2015 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

import ww3forecast

def preprocess():
    ds = ww3forecast.ww3forecast()
    ds.batchprocess()

if __name__ == "__main__":
    preprocess()
