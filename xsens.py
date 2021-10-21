#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mon Oct 11 11:31:51 2021.

@author: michael
"""

# Standard packackes
from tqdm import tqdm
import geopandas as gpd
import os

# Local Packages: Parser
from lib import ParseXsens
from lib import theo_df
from lib import xsense_df

# Local Packages: Tools
from lib import geolib as gl
from lib import timetools as tt
from lib import input_

# Local Packages: Plots
from lib.plot import plot_trace

# =============================================================================
# Local variables
# =============================================================================

# Xsens
shpFileXsens = './data/xsens/18_03_2021/xsens_trace_18_03_2021.shp'
xsens_dir = './data/xsens/18_03_2021/snmea/'
file_xsens = './data/xsens/18_03_2021/snmea/xsens_18_03_2021.snmea'

# Theodolites
root5a, _ = os.path.splitext(input_.fileTheo5a)
root5b, _ = os.path.splitext(input_.fileTheo5b)
shpFileTheo5a = root5a + '.shp'
shpFileTheo5b = root5b + '.shp'

# Load rails als shapefile
rail_back = gpd.read_file(input_.rail_back)
rail_forth = gpd.read_file(input_.rail_forth)

# Local Parameters
do_parse = False
save = False
do_trace = False
columns = ['timestamp', 'lon', 'lat', 'alt']    # Extract only wnated paramters


# =============================================================================
# Local Functions
# =============================================================================
# Load Xsens Data
def parse(out_dir: str, save: bool):
    """Parse and return df. if save=True save ''.txt into ''.snema data."""
    # TODO: replace range(10) by range number of .text files in folder
    print('\n\n')
    for _n in range(11):
        _num = str(_n).zfill(2)
        # TODO: move filepath to input an use os.tail head
        out_file = out_dir + 'xsens_' + _num + '.snmea'
        filepath = './data/xsens/18_03_2021/source/converted/xsens_' \
            + _num + '.txt'
        if _n == 0:
            df = ParseXsens(filepath, out_file, save=save).main()
        else:
            df_new = ParseXsens(filepath, out_file, save=save).main()
            df.append(df_new)
    print('\n')
    return df


def load():
    """Load xsens.snmea files into one single dataframe."""
    # TODO: replace range(10) by range number of .text files in folder
    print('\n\n')
    for _n in range(11):
        _num = str(_n).zfill(2)
        filepath = './data/xsens/18_03_2021/snmea/mn95_xsens_' + _num + \
            '.snmea'
        if _n == 0:
            print('Loading : ', filepath)
            df, valid = xsense_df(filepath, columns=columns)
        else:
            print('Loading : ', filepath)
            df_new, valid = xsense_df(filepath, columns=columns)
            df = df.append(df_new)
    print('\n')
    return df, valid


# =============================================================================
# Load Xsens data
# =============================================================================

# Load xsens dataframe
if do_parse:
    df = parse(xsens_dir, save)
df, valid = load()

# Change time format
df['timestamp'] = df['timestamp'].map(lambda x: tt.utcrcf3339(str(x)))

# OPTIMIZE: very very slow process because HUUuuge file size
if do_trace:
    print('Drawing xsens trace : ', shpFileXsens)
    xsens_shp = gl.pt2shpline(df=df, shpfile_out=shpFileXsens)

# =============================================================================
# Xsens: Exploratory analysis
# =============================================================================

# print('Plotting xsens trace')
# plot_trace(rail_shp_path=rail_forth, shp_path=shpFileXsens,
#            receiver_name='xsens', df=df)

# =============================================================================
# Load References: theodolites, rail
# =============================================================================
# Extract theodolites data into dataframe
print('Load Theodolites dataframe')
df5a, _ = theo_df(input_.fileTheo5a, columns)
df5b, _ = theo_df(input_.fileTheo5b, columns)

# # Create line for the theodolites measures
# print('Create Trace of the Theodolites')
# t5a_shp = gl.pt2shpline(df=df5a, shpfile_out=shpFileTheo5a)
# t5b_shp = gl.pt2shpline(df=df5b, shpfile_out=shpFileTheo5b)

# =============================================================================
# Xsens Precision (A): Theodolites
# =============================================================================
# Get distance from thedolites shape LINE
df_sync = tt.sync(df, df5a,
                  time_format1='%Y-%m-%dT%H:%M:%S.%fZ',
                  time_format2='%Y-%m-%dT%H:%M:%S.%fZ')

# Reset Index
df_sync = df_sync[~df_sync['timestamp'].isna()].reset_index()

# Measure distance between POINT and reference LINE
df_sync = gl.distance_df2shpfile(df_sync, x='lon', y='lat',
                                 shpfile=shpFileTheo5a)
df5b = gl.distance_df2shpfile(df5b, x='lon', y='lat', shpfile=shpFileTheo5b)

# =============================================================================
# Xsens Precision (B): Railways
# =============================================================================
# Split Track
track_index = gl.split_track(df)

# Mesure distance to the reference rail
loop = tqdm(total=100, position=0, desc='Calculating distances')
for track in track_index:
    df = gl.dist2rail(df[track[0]:track[1]], rail_back, rail_forth)
    loop.update(1)
loop.close()
