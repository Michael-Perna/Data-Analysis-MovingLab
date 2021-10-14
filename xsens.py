#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mon Oct 11 11:31:51 2021.

@author: michael
"""

from lib import ParseXsens
from lib import theo_df
from lib import xsense_df

from lib import global_
from lib import geolib as gl
from lib import timetools as tt

import os

# =============================================================================
# Local variables
# =============================================================================
do_parse = False
save = True
columns = ['timestamp', 'lon', 'lat']


# =============================================================================
# Local Function
# =============================================================================
# Load Xsens Data
def parse(save: bool):
    """Parse and return df. if save=True save ''.txt into ''.snema data."""
    # TODO: replace range(10) by range number of .text files in folder
    for _n in range(11):
        _num = str(_n).zfill(2)
        # TODO: move filepath to input an use os.tail head
        filepath = './data/xsens/18_03_2021/xsens_' + _num + '.txt'
        if _n == 0:
            df = ParseXsens(filepath, save=save).main()
        else:
            df_new = ParseXsens(filepath, save=save).main()
            df.append(df_new)
    return df


def load():
    """Load xsens.snmea files into one single dataframe."""
    # TODO: replace range(10) by range number of .text files in folder
    for _n in range(11):
        _num = str(_n).zfill(2)
        filepath = './data/xsens/18_03_2021/snmea/xsens_' + _num + '.snmea'
        if _n == 0:
            df, valid = xsense_df(filepath, columns=columns)
        else:
            df_new, valid = xsense_df(filepath, columns=columns)
            df = df.append(df_new)
    return df, valid


# =============================================================================
# Main
# =============================================================================
# Load references
shpFileRail = './maps/railways/foward_track_adjusted.shp'
FileTheo5a = './data/theodolites/trajectoire_5_st1.txt'
FileTheo5b = './data/theodolites/trajectoire_5_st2.txt'
root5a, _ = os.path.splitext(FileTheo5a)
root5b, _ = os.path.splitext(FileTheo5b)
shpFileTheo5a = root5a + '.shp'
shpFileTheo5b = root5b + '.shp'
# shpFileXsense =

# Extract theodolites data into dataframe
df5a, _ = theo_df(FileTheo5a, columns)
df5b, _ = theo_df(FileTheo5b, columns)

# Get distance from shape LINE
# df5a = gl.distance_df2shpfile(df5a, x='lon', y='lat', shpfile=shpFileTheo5a)
# df5b = gl.distance_df2shpfile(df5b, x='lon', y='lat', shpfile=shpFileTheo5b)

# create line for the theodolites measures
t5a_shp = gl.pt2shpline(df=df5a, shpfile_out=shpFileTheo5a)
t5b_shp = gl.pt2shpline(df=df5b, shpfile_out=shpFileTheo5b)

# Load xsens dataframe
if do_parse:
    df = parse(save)
df, valid = load()

# Get distance from thedolites shape LINE
df_sync = tt.sync(df, df5a,
                  time_format1='%Y-%m-%dT%H:%M:%S.%fZ',
                  time_format2='%Y-%m-%dT%H:%M:%S.%fZ')
df_sync = df_sync[~df_sync['timestamp'].isna()].reset_index()
df_sync = gl.distance_df2shpfile(df_sync, x='lon', y='lat',
                                 shpfile=shpFileTheo5a)
# df5b = gl.distance_df2shpfile(df5b, x='lon', y='lat', shpfile=shpFileTheo5b)


# create shape line from the xsens measures

# Used it to compare receiver on the whole traject

# Make some nice plot
