#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Tue Oct 19 14:22:00 2021.

@author: michael
"""

# Standard modules
from tqdm import tqdm
import numpy as np
import pandas as pd


def _is_inbox(x: float, y: float, box: list):
    """Answer True if the point (x,y) is inside the 'box'."""
    if x > box[0, 0] and x < box[1, 0]:
        if y > box[0, 1] and y < box[1, 1]:
            return True
    else:
        return False


def _is_inloop(x: float, y: float):
    """
    Check if the point is inside a rail loop.

    Parameters
    ----------
    x : float
        Longitute in MN95 reference frame.
    y : float
        Latitude in MN95 reference frame.

    Returns
    -------
    Boolean
        True if the point (x,y) is inside a Terminal loop of the tram 12 of
        the TPG (Transport Public Genevois).

    """
    box1 = np.matrix('2498300, 1114715; 2498361, 1114780')
    box2 = np.matrix('2498762, 1114269; 2498820, 1114307')
    box3 = np.matrix('2499583, 1114983; 2499652, 1115047')
    box4 = np.matrix('2504780, 1116346; 2504949, 1116475')
    # box5 =  np.matrix('2498977, 1114431; 2499183, 1114749')

    return _is_inbox(x, y, box1) or _is_inbox(x, y, box2) \
        or _is_inbox(x, y, box3) or _is_inbox(x, y, box4)
    # or _is_inbox(x,y,box5)


def split_track(df_full):
    """Split the data series in track data that are on the same rail.

    Description
    -----------
        This method cann be applied as the tram follow a growing longitude
        path (or viceversa decreasing).

        The 'track_index':  is a matrix with:

            num°Track: index_start, index_end
            ---------------------------------
              0         52            11120
    """
    lon = pd.DataFrame(df_full['lon']).to_numpy()
    lat = pd.DataFrame(df_full['lat']).to_numpy()

    # Loop initialization
    loop = tqdm(total=len(lon)-4, desc="Dividing full track ..", position=0)
    track_index = np.zeros((100, 2)).astype(int)     # 100 i a guess
    n = 0
    _start = False

    for i in range(len(lon)-4):
        # START (quitting the loop)
        if _is_inloop(lon[i], lat[i]) and not _is_inloop(lon[i+1], lat[i+1]):
            track_index[n, 0] = i
            _start = True

        # STOP (entering the loop)
        if not _is_inloop(lon[i], lat[i]) and _is_inloop(lon[i+1], lat[i+1]):
            # STOP
            track_index[n, 1] = i
            n += 1
            _start = False

        delta = df_full['timestamp'].iloc[i+1]-df_full['timestamp'].iloc[i]

        # If the there is a time gap great than five minutes break
        if delta.total_seconds() > 300 and _start is True:
            track_index[n, 1] = i
            n += 1

            # Start
            track_index[n, 0] = i + 1

        # Progress bar:
        loop.update(1)

    # Last track end index
    track_index[n, 1] = i

    loop.close()

    # Remove empty line from track_index
    mask = track_index.any(axis=1)
    track_index = track_index[mask]
    track_index = track_index.astype(int)

    return track_index


def classify_track(df):
    """
    Assign an orientation to each track.

    Parameters
    ----------
    df : dataframe
        dataframe containing track data.

    Returns
    -------
    track: str
        'backward': the tram is moving from the station Moisullaz to Bachet
        'foward':   the tram is moving from the station Bachet to Moisullaz

    """
    # remove nan position
    small_df = df.dropna(subset=['lat', 'lon']).reset_index(drop=False)

    if small_df.empty or len(small_df) <= 1:
        return 'too small'
    # look at first longitude
    first = small_df['lon'].iloc[1]
    # look at last longitude
    last = small_df['lon'].iloc[-1]

    # Define the track orientation
    if first > last:
        track = 'backward'
    elif first < last:
        track = 'foward'
    else:
        print('Huston we have a problem!')
        return 'problem'
    return track
