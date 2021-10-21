#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 15:00:48 2021.

@author: michael
"""

# Import standard module
import geopandas as gpd
import math
import os

# Import local module
from lib.geolib import find_tramway
from lib import geolib as gl


# Local Functions
def _create_folder(folder_name: str):
    """Make directory if it does not exist."""
    if not os.path.isdir(folder_name):
        os.makedirs(folder_name)
        print("created folder : ", folder_name)


def save_track(df: object, file_name: str):
    """Save track dataframe with start and end time."""
    start = df['timestamp'].iloc[0].strftime('%H_%M_%S')
    end = df['timestamp'].iloc[-1].strftime('%H_%M_%S')

    folder_name, file_name = os.path.split(file_name)
    folder_name = folder_name + '/tracks/'
    head, _ = os.path.splitext(file_name)

    _create_folder(folder_name)

    file_name = folder_name + head + '__' + start + '_' + end + ".results"

    df.to_csv(file_name, sep=',', na_rep='', header=False, index=False,
              line_terminator='\n')


def save_all(df: object, filename: str):
    """Save the entire dataframe with start and end time."""
    # skip csv with less than one epoch
    if df.empty or len(df) <= 1:
        return

    root, tail = os.path.split(filename)
    head, _ = os.path.splitext(tail)
    folder_name = root + '/tracks/'

    # save the entire dataframe as a csv file
    folder_name = folder_name + 'csv/'
    # if the directory does not exist it create it
    if not os.path.isdir(folder_name):
        os.makedirs(folder_name)

    df.to_csv(folder_name + head + ".csv", index=False)


def get_distance(df: object, rail_back: object, rail_forth: object):
    """Loop over each track calculate the GNSS error and save the track."""
    # Reset index
    df = df.reset_index(drop=True)

    # skip csv with less than one epoch
    if df.empty or len(df) <= 1:
        pass

    # -------------------------------------------------------------------------
    # Load rails als shapefile
    # -------------------------------------------------------------------------
    # rail_back = gpd.read_file(input_.rail_forth)
    # rail_forth = gpd.read_file(input_.rail_back)

    # -------------------------------------------------------------------------
    # Identify the tramway in the railway
    # -------------------------------------------------------------------------
    track_type = find_tramway.classify_track(df)

    # -------------------------------------------------------------------------
    # Create POINT Geometry from Lon/Lat
    # -------------------------------------------------------------------------
    gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))

    # -------------------------------------------------------------------------
    # Mesure orthoigonal distance between POINT and the rail reference
    # -------------------------------------------------------------------------
    dist = [None]*len(df['geometry'])
    if track_type == 'foward':
        for index, row in df.iterrows():
            if not math.isnan(row['geometry'].x) \
                    or not math.isnan(row['geometry'].x):
                dist[index] = gl.distance_pt2shpline(
                    row['geometry'], rail_forth)
        df['dist'] = dist
        return df
    elif track_type == 'backward':
        for index, row in df.iterrows():
            if not math.isnan(row['geometry'].x) \
                    or not math.isnan(row['geometry'].x):
                dist[index] = gl.distance_pt2shpline(
                    row['geometry'], rail_back)
        df['dist'] = dist
        return df
    elif track_type == 'too small':
        df = []
        return df
    else:
        print('there is a problem')
