#!/usr/bin/env python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Matthew Howie

import numpy as np

def meanbearing(wdir):
    '''Returns the mean true bearing of an array of true bearings.

       Arguments:
       wdir -- An array of angles between 0 and 360. (NumPy Array)

       Returns:
       bearing --  Mean bearing of the angles contained in array wdir. (float)
       '''
    #initialize x,y,wavedir
    x,y = 0, 0
    wavedir = wdir  
    for i in range(len(wavedir)):
       #convert to radians
       a = float(wavedir[i])
       a = a*((np.pi)/180.0)
       #disagreegate angles into x,y components
       y = y + np.sin(a)
       x = x + np.cos(a) 
    #calculate mean bearing by taking the inverse tangent of y/xi
    bearing = np.arctan2(y,x)
    #arctan2 returns range -pi,pi rather than 0,2pi, so conversion is required if < 0.
    if bearing < 0:
        bearing = bearing + 2*np.pi
    
    return bearing
