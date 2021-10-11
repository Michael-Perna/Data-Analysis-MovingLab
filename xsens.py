#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 11 11:31:51 2021.

@author: michael
"""

from lib import ParseXsens
from lib import ParseTheo

# Load Xsens Data
for _n in range(10):
    _num = str(_n).zfill(2)
    filepath = './data/18_03_2021/xsens_' + _num + '.txt'
    if _n == 0:
        df = ParseXsens(filepath, save=False).main()
    else:
        df_new = ParseXsens(filepath, save=False).main()
        df.append(df_new)

# Load references
shpFileRail = './maps/railways/foward_track_adjusted.shp'
FileTheo = './data/trajectoire_5_st1.txt'
shpFileTheo = './data/trajectoire_5_st1.shp'

# create line from the theodolites measures
df5a = ParseTheo(base + 'trajectoire_5_st1.txt', shpFileTheo).main()
df5b = ParseTheo(base + 'trajectoire_5_st2.txt', shpFileTheo).main()

# Get distance from shape LINE
df = distance_df2shpfile(df5a, x='lon', y='lat', shpfile=shpFileTheo)
# df = distance_df2shpfile(df5a, x='lon', y='lat', shpFileTheo)
# df = distance_df2shpfile(df5a, x='lon', y='lat', shpFileTheo)

# Used it to compare receiver on the whole traject

# Make some nice plot
