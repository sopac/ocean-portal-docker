#!/usr/bin/env python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Matthew Howie

def dirflip(wdir):
    '''Returns wdir angles flipped by 180 degrees (this is useful for switching between oceanographic and meteorologic direction conventions)

       Arguments:
       wdir -- an array of angles between 0 and 360. (NumPy Array)

       Returns:
       wdir -- an array of angles between 0 and 360 flipped by 180 with respect to input array. (NumPy Array)
    '''
    for i in range(len(wdir)):
        #flip first and 2nd half of polar coords independently to maintain (0,360) range
        if wdir[i] > 180:
            wdir[i] = wdir[i] - 180
        elif wdir[i] < 180:
            wdir[i] = wdir[i] + 180
        #account for crossover points
        elif wdir[i] == 180:
            wdir[i] = 0
        elif wdir[i] == 0:
            wdir[i] = 180
    return wdir

def dirshift(wdir):
    '''Changes wdir angular defintion from (0,360) to (-22.5 337.5).

       Argument:
       wdir -- an array of angular values between 0 and 360. (NumPy Array)

       Returns:
       wdir -- an array of angular values between -22.5 and 337.5. (NumPy Array)
       '''
    for i in range(len(wdir)):
        if wdir[i] >= 337.5:
            wdir[i] = wdir[i] - 360
        else:
            continue
    return wdir
