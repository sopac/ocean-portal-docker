#!/usr/bin/env python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Jason Smith <jason.smith@bom.gov.au>

import matplotlib.pyplot as plt
import matplotlib
import scipy as sci
import scipy.stats

def stddev_colors(wheight,wavg,stddev,Nmax):
    '''returns a discretised colormap based on standard deviations of wheight.

       Arguments:
       wheight -- An array of values for calculated standard deviations.  (NumPy Array)
       wavg -- mean of the values in wheight.  (float)
       stddev -- Standard deviation of the values in wheight. (float)
       Nmax -- Maximum value in wheight.  (float)

       Returns:
       my_cmap -- colormap based on standard deviations of wheight data.
    '''

    std1lower = round(sci.stats.scoreatpercentile(wheight,15.9),2)
    std1upper = round(sci.stats.scoreatpercentile(wheight,84.1),2)
    std2lower = round(sci.stats.scoreatpercentile(wheight,2.25),2)
    std2upper = round(sci.stats.scoreatpercentile(wheight,97.75),2)
    std3lower = round(sci.stats.scoreatpercentile(wheight,0.15),2)
    std3upper = round(sci.stats.scoreatpercentile(wheight,99.85),2)

    wavgnorm = wavg/Nmax
    sd1upp = std1upper/Nmax
    sd1low = std1lower/Nmax
    sd2upp = std2upper/Nmax
    sd2low = std2lower/Nmax
    sd3low = std3lower/Nmax
    sd3upp = std3upper/Nmax

    print wavgnorm

    cdict = {'red':((0.0,  0.0, 0.0),
                    (sd3low, 0.0, 1.0),
                    (sd2low, 1.0, 0.0),
                    (sd1low, 0.0, 0.0),
                    (sd1upp, 0.0, 0.0),
                    (sd2upp, 0.0, 1.0),
                    (sd3upp, 1.0, 0.0),
                    (1.0, 0.0, 0.0)),

         'green':  ((0.0,  0.0, 0.0),
                    (sd3low, 0.0, 0.0),
                    (sd2low, 0.0, 1.0),
                    (sd1low, 1.0, 0.0),
                    (sd1upp, 0.0, 1.0),
                    (sd2upp, 1.0, 0.0),
                    (sd3upp, 0.0, 0.0),
                    (1.0, 0.0, 0.0)),

         'blue':   ((0.0,  0.0, 0.0),
                    (sd3low, 0.0, 0.0),
                    (sd2low, 0.0, 0.0),
                    (sd1low, 0.0, 1.0),
                    (sd1upp, 1.0, 0.0),
                    (sd2upp, 0.0, 0.0),
                    (sd3upp, 0.0, 0.0),
                    (1.0, 0.0, 0.0))}

    my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, 1024)

    return(my_cmap)

def decile_rose():
    '''Return a discretised color map divided into deciles of wheight.

       Arguments:
       wheight --  Histogram of wave data for calculation of deciles (NumPy Histogram).
       wavg -- Mean value of wheight histogram (float).
       Nmax --  Maximum value in wheight histogram (float).

       Returns:
       my_cmap -- A colormap discretised by deciles of wheight data.
       '''

    cdict = {'red':((0.0,  0.0, 1.0),
                    (0.1, 1.0, 1.0),
                    (0.2, 1.0, 1.0),
                    (0.3, 1.0, 0.0),
                    (0.4, 0.0, 0.0),
                    (0.5, 0.0, 0.8),
                    (1.0, 0.8, 0.0)),

         'green':  ((0.0,  0.0, 0.0),
                    (0.1, 0.0, 0.5),
                    (0.2, 0.5, 1.0),
                    (0.3, 1.0, 1.0),
                    (0.4, 1.0, 0.5),
                    (0.5, 0.5, 0.0),
                    (1.0, 0.0, 0.0)),


         'blue':   ((0.0,  0.0, 0.0),
                    (0.1, 0.0, 0.0),
                    (0.2, 0.0, 0.0),
                    (0.3, 0.0, 0.0),
                    (0.4, 0.0, 1.0),
                    (0.5, 1.0, 0.8),
                    (1.0, 0.8, 0.0))}

    my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, 1024)

    return(my_cmap)

def decile_colors(wheight,Nmax):
    '''Return a discretised color map divided into deciles of wheight.

       Arguments:
       wheight --  Histogram of wave data for calculation of deciles (NumPy Histogram).
       wavg -- Mean value of wheight histogram (float).
       Nmax --  Maximum value in wheight histogram (float).

       Returns:
       my_cmap -- A colormap discretised by deciles of wheight data.
       '''

    d1 = round(sci.stats.scoreatpercentile(wheight,10),2)
    d2 = round(sci.stats.scoreatpercentile(wheight,20),2)
    d3 = round(sci.stats.scoreatpercentile(wheight,30),2)
    d4 = round(sci.stats.scoreatpercentile(wheight,40),2)
    d5 = round(sci.stats.scoreatpercentile(wheight,50),2)
    d6 = round(sci.stats.scoreatpercentile(wheight,60),2)
    d7 = round(sci.stats.scoreatpercentile(wheight,70),2)
    d8 = round(sci.stats.scoreatpercentile(wheight,80),2)
    d9 = round(sci.stats.scoreatpercentile(wheight,90),2)

    d1n = d1/Nmax
    d2n = d2/Nmax
    d3n = d3/Nmax
    d4n = d4/Nmax
    d5n = d5/Nmax
    d6n = d6/Nmax
    d7n = d7/Nmax
    d8n = d8/Nmax
    d9n = d9/Nmax

    cdict = {'red':((0.0,  0.0, 1.0),
                    (d1n, 1.0, 1.0),
                    (d2n, 1.0, 1.0),
                    (d3n, 1.0, 0.75),
                    (d4n, 0.75, 0.0),
                    (d5n, 0.0, 0.0),
                    (d6n, 0.0, 0.0),
                    (d7n, 0.0, 0.0),
                    (d8n, 0.0, 0.5),
                    (d9n, 0.5, 1.0),
                    (1.0, 1.0, 0.0)),

         'green':  ((0.0,  0.0, 0.0),
                    (d1n, 0.0, 0.5),
                    (d2n, 0.5, 1.0),
                    (d3n, 1.0, 1.0),
                    (d4n, 1.0, 1.0),
                    (d5n, 1.0, 1.0),
                    (d6n, 1.0, 0.5),
                    (d7n, 0.5, 0.0),
                    (d8n, 0.0, 0.0),
                    (d9n, 0.0, 0.0),
                    (1.0, 0.0, 0.0)),

         'blue':   ((0.0,  0.0, 0.0),
                    (d1n, 0.0, 0.0),
                    (d2n, 0.0, 0.0),
                    (d3n, 0.0, 0.0),
                    (d4n, 0.0, 0.0),
                    (d5n, 0.0, 0.5),
                    (d6n, 0.5, 1.0),
                    (d7n, 1.0, 1.0),
                    (d8n, 1.0, 1.0),
                    (d9n, 1.0, 1.0),
                    (1.0, 1.0, 0.0))}

    my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, 1024)

    return(my_cmap)

def quartile_colors(wheight,wavg,Nmax,binwd):
    '''Returns a discretised colormap divided by quartiles of wheight.

       Arguments:
       wheight -- Histogram of wave data to calculate quartiles (NumPy Histogram).
       wavg -- Mean value of wheight histogram (float).
       Nmax -- Maximum value of wheight histogram (float).
       binwd -- bin width of wheight histogram (float).

       Returns:
       my_cmap -- A  colormap discretised by quartiles of wheight data.
       '''

    q1 = round(sci.stats.scoreatpercentile(wheight,25),2)
    q2 = round(sci.stats.scoreatpercentile(wheight,50),2)
    q3 = round(sci.stats.scoreatpercentile(wheight,75),2)

    wavgnorm = wavg/Nmax
    adjuster = 0.05*binwd

    q1n = q1/Nmax - (adjuster)
    q2n = q2/Nmax - (adjuster)
    q3n = q3/Nmax - (adjuster)

    cdict = {'red':((0.0,  0.0, 1.0),
                    (q1n, 1.0, 0.0),
                    (q2n, 0.0, 0.0),
                    (q3n, 0.0, 0.0),
                    (1.0, 0.0, 0.0)),

         'green':  ((0.0,  0.0, 0.0),
                    (q1n, 0.0, 0.5),
                    (q2n, 0.5, 0.5),
                    (q3n, 0.5, 0.0),
                    (1.0, 0.0, 0.0)),

         'blue':   ((0.0,  0.0, 0.0),
                    (q1n, 0.0, 0.0),
                    (q2n, 0.0, 0.0),
                    (q3n, 0.0, 1.0),
                    (1.0, 1.0, 0.0))}

    my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, 1024)

    return(my_cmap)

def quartoutlier_colors(wheight,wavg,Nmax,binwd):
    '''Returns a discretised colormap of quartiles plus outliers of wheight.

       Arguments:
       wheight -- histogram of values to calculate quartiles (NumPy Histogram)
       wavg -- mean value of wheight. (float)
       Nmax -- maximum value of wheight.  (float)
       binwd -- histogram bin width.  (float)

       Returns:
       my_cmap --  A colormap, discretised by quartiles of wheight data.
       '''
    #calculate quartiles, interquartile range and rogue wave height
    q1 = round(sci.stats.scoreatpercentile(wheight,25),2)
    q2 = round(sci.stats.scoreatpercentile(wheight,50),2)
    q3 = round(sci.stats.scoreatpercentile(wheight,75),2)
    IQ = round(q3-q1,2)
    #o1 = round(q1 - 1.5*IQ,2)
    o2 = round(2*wavg,2)
    #normalizard average
    wavgnorm = wavg/Nmax
    #adjuster value used for normalization
    adjuster = 0.05*binwd
    #normalize quartiles into range (0,1)
    q1n = q1/Nmax-(adjuster)
    q2n = q2/Nmax-(adjuster)
    q3n = q3/Nmax-(adjuster)
    #o1n = o1/Nmax-(adjuster)
    o2n = o2/Nmax-(adjuster)
    #determine the colors over different regions of histogram specified by quartiles
    cdict = {'red':((0.0,  0.0, 1.0),
                    #(o1n, 0.0, 1.0),
                    (q1n, 1.0, 0.0),
                    (q2n, 0.0, 0.0),
                    (q3n, 0.0, 0.0),
                    (o2n, 0.0, 0.0),
                    (1.0, 0.0, 0.0)),

         'green':  ((0.0,  0.0, 0.0),
                    #(o1n, 0.0, 1.0),
                    (q1n, 0.0, 0.5),
                    (q2n, 0.5, 0.5),
                    (q3n, 0.5, 0.0),
                    (o2n, 0.0, 0.0),
                    (1.0, 0.0, 0.0)),

         'blue':   ((0.0,  0.0, 0.0),
                    #(o1n, 0.0, 1.0),
                    (q1n, 0.0, 0.0),
                    (q2n, 0.0, 0.0),
                    (q3n, 0.0, 1.0),
                    (o2n, 1.0, 0.0),
                    (1.0, 0.0, 0.0))}

    my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, 1024)

    return(my_cmap)

def tercile_colors(wheight,wavg,Nmax,binwd):
    '''Returns a discretised colormap of quartiles plus outliers of wheight.

       Arguments:
       wheight -- histogram of values to calculate quartiles (NumPy Histogram)
       wavg -- mean value of wheight. (float)
       Nmax -- maximum value of wheight.  (float)
       binwd -- histogram bin width.  (float)

       Returns:
       my_cmap --  A colormap, discretised by quartiles of wheight data.
       '''
    #calculate quartiles, interquartile range and rogue wave height
    q1 = round(sci.stats.scoreatpercentile(wheight,33.33),2)
    q2 = round(sci.stats.scoreatpercentile(wheight,50),2)
    q3 = round(sci.stats.scoreatpercentile(wheight,66.67),2)
    IQ = round(q3-q1,2)
    #o1 = round(q1 - 1.5*IQ,2)
    o2 = round(2*wavg,2)
    #normalizard average
    wavgnorm = wavg/Nmax
    #adjuster value used for normalization
    adjuster = 0.05*binwd
    #normalize quartiles into range (0,1)
    q1n = q1/Nmax-(adjuster)
    q2n = q2/Nmax-(adjuster)
    q3n = q3/Nmax-(adjuster)
    #o1n = o1/Nmax-(adjuster)
    o2n = o2/Nmax-(adjuster)
    #determine the colors over different regions of histogram specified by quartiles
    cdict = {'red':((0.0,  0.0, 1.0),
                    #(o1n, 0.0, 1.0),
                    (q1n, 1.0, 0.0),
                    (q2n, 0.0, 0.0),
                    (q3n, 0.0, 0.0),
                    (o2n, 0.0, 0.0),
                    (1.0, 0.0, 0.0)),

         'green':  ((0.0,  0.0, 0.0),
                    #(o1n, 0.0, 1.0),
                    (q1n, 0.0, 0.5),
                    (q2n, 0.5, 0.5),
                    (q3n, 0.5, 0.0),
                    (o2n, 0.0, 0.0),
                    (1.0, 0.0, 0.0)),

         'blue':   ((0.0,  0.0, 0.0),
                    #(o1n, 0.0, 1.0),
                    (q1n, 0.0, 0.0),
                    (q2n, 0.0, 0.0),
                    (q3n, 0.0, 1.0),
                    (o2n, 1.0, 0.0),
                    (1.0, 0.0, 0.0))}

    my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, 1024)

    return(my_cmap)

def tercoutlier_colors(wheight,wavg,Nmax,binwd):
    '''Returns a discretised colormap of quartiles plus outliers of wheight.

       Arguments:
       wheight -- histogram of values to calculate quartiles (NumPy Histogram)
       wavg -- mean value of wheight. (float)
       Nmax -- maximum value of wheight.  (float)
       binwd -- histogram bin width.  (float)

       Returns:
       my_cmap --  A colormap, discretised by quartiles of wheight data.
       '''
    #calculate quartiles, interquartile range and rogue wave height
    q1 = round(sci.stats.scoreatpercentile(wheight,33.33),2)
    q2 = round(sci.stats.scoreatpercentile(wheight,50),2)
    q3 = round(sci.stats.scoreatpercentile(wheight,66.67),2)
    IQ = round(q3-q1,2)
    #o1 = round(q1 - 1.5*IQ,2)
    o2 = round(2*wavg,2)
    #normalizard average
    wavgnorm = wavg/Nmax
    #adjuster value used for normalization
    adjuster = 0.05*binwd
    #normalize quartiles into range (0,1)
    q1n = q1/Nmax-(adjuster)
    q2n = q2/Nmax-(adjuster)
    q3n = q3/Nmax-(adjuster)
    #o1n = o1/Nmax-(adjuster)
    o2n = o2/Nmax-(adjuster)
    #determine the colors over different regions of histogram specified by quartiles
    cdict = {'red':((0.0,  0.0, 1.0),
                    #(o1n, 0.0, 1.0),
                    (q1n, 1.0, 0.0),
                    (q2n, 0.0, 0.0),
                    (q3n, 0.0, 0.0),
                    (o2n, 0.0, 0.0),
                    (1.0, 0.0, 0.0)),

         'green':  ((0.0,  0.0, 0.0),
                    #(o1n, 0.0, 1.0),
                    (q1n, 0.0, 0.5),
                    (q2n, 0.5, 0.5),
                    (q3n, 0.5, 0.0),
                    (o2n, 0.0, 0.0),
                    (1.0, 0.0, 0.0)),

         'blue':   ((0.0,  0.0, 0.0),
                    #(o1n, 0.0, 1.0),
                    (q1n, 0.0, 0.0),
                    (q2n, 0.0, 0.0),
                    (q3n, 0.0, 1.0),
                    (o2n, 1.0, 0.0),
                    (1.0, 0.0, 0.0))}

    my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, 1024)

    return(my_cmap)
