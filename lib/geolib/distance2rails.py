#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 15:00:48 2021.

@author: michael
"""

# Import standard module
from numpy.linalg import norm
import geopandas as gpd
import numpy as np
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


def _angle_Eaxis_yAxis(pproj, point):
    """
    Calculate rotation angle of the error ellipse in the tramway frame.

    Description
    ----------
    get the orientation of the major axis on the"local Tram" Frame :
    the orientation of the semi-major axis of error ellipse
    is given in degrees from true north and has values in the range
    [0,180]

    Parameters
    ----------
    pproj : TYPE
        Projected point on the railway reference.
    point : TYPE
        Measured point by the GNSS receiver.

    Returns
    -------
    angle float
        Angle of rotation between the major axis of error ellipse in MN95
        reference frame and the tramway reference frame.

    """
    n1 = np.array([1, 0])
    x2 = point.coords[0][0] - pproj.coords[0][0]
    y2 = point.coords[0][1] - pproj.coords[0][1]
    d = np.array([x2, y2])
    n2 = d / norm(d)

    angle = np.arctan(np.dot(n1, n2)/(norm(n1)*norm(n2)))
    angle = np.degrees(angle)
    return angle


def _projectionOnLateralTramAxe(stdLong: float, stdLat: float,
                                point, pproj):
    """
    Project the standardt deciation on the tramway reference frame.

    Parameters
    ----------
    stdLong : float
        standardt deviation on the longitude axis.
    stdLat : float
        standardt deviation on the Latitute axis.
    point : TYPE
        Projected point on the railway reference.
    pproj : TYPE
        Measured point by the GNSS receiver.

    Returns
    -------
    Sy_TramAxe : float
        Projected standard deviation on the y-axis of the tram reference frame
        (parallel to the running direction).
    Sx_TramAxe : float
        Projected standard deviation on the x-axis of the tram reference frame
        (perpendicular to the running direction).
    alpha : float
        Angle of rotation between the major axis of error ellipse in MN95
        reference frame and the tramway reference frame.[degrees]

    """
    alpha = _angle_Eaxis_yAxis(pproj, point)

    # conversion in radiant
    r_alpha = np.radians(alpha)

    # First apply rotation then nimmt |.|
    Sy_TramAxe = np.sqrt((stdLong*np.cos(r_alpha)) **
                         2 + (stdLat*np.sin(r_alpha))**2)
    Sx_TramAxe = np.sqrt((stdLong*np.sin(r_alpha)) **
                         2 + (stdLat*np.cos(r_alpha))**2)

    return Sy_TramAxe, Sx_TramAxe, alpha


def errors(stdLon, stdLat, point, polyline):
    """
    Estimate GNSS error given a line of reference and the standard deviation.

    Parameters
    ----------
    stdLong : float
        standardt deviation on the longitude axis.
    stdLat : float
        standardt deviation on the Latitute axis.
    point : TYPE
        Projected point on the railway reference.
    polyline : LINE object
        LINE object which define the reference of the railwayas.

    Returns
    -------
    dist : float
        DESCRIPTION.
    err : flot
        DESCRIPTION.
    pp : TYPE
        DESCRIPTION.
    Sy_TramAxe : float
        Projected standard deviation on the y-axis of the tram reference frame
        (parallel to the running direction).
    Sx_TramAxe : float
        Projected standard deviation on the x-axis of the tram reference frame
        (perpendicular to the running direction).
    alpha : float
        Angle of rotation between the major axis of error ellipse in MN95
        reference frame and the tramway reference frame.[degrees]

    """
    # Distance = norm(point-pp)
    dist, pp = gl.distance_pt2shpline(point, polyline, point_proj=True)

    Sy, Sx, alpha = _projectionOnLateralTramAxe(stdLon, stdLat, point, pp)

    err = dist / Sy

    # Change scale from meter to 10 nm
    alpha = round(alpha, 5)
    err = round(err, 4)
    dist = round(dist, 3)
    Sy = (Sy).round(decimals=4)
    Sx = (Sx).round(decimals=4)

    return dist, err, pp, Sy, Sx, alpha


def dist2rail(df: object, rail_back: object, rail_forth: object):
    """Loop over each track calculate the GNSS error and save the track."""
    # Reset index
    df = df.reset_index(drop=True)

    # skip csv with less than one epoch
    if df.empty or len(df) <= 1:
        pass

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


def err2rail(df: object, rail_back: object, rail_forth: object):
    """Loop over each track calculate the GNSS error and save the track.

    Description
    -----------
    Get information about the GNSS mesure errors.

    "dist" :  orthogonal distance between point and rail
              which is the absolute errors of the GNSS
              point

    "pproj":  projection of the GNSS point onto the rail
              line

    "err":    standarized absolute errors.
              err = dist / Sy


    "Sy":      Is

    "alpha":   angle between the y-axis (perpendicular to
               the rail) and E-axis
    """
    # Reset index
    df = df.reset_index(drop=True)

    # skip csv with less than one epoch
    if df.empty or len(df) <= 1:
        pass

    # -------------------------------------------------------------------------
    # Identify the tramway in the railway
    # -------------------------------------------------------------------------
    track_type = find_tramway.classify_track(df)

    # -------------------------------------------------------------------------
    # Create POINT Geometry from Lon/Lat
    # -------------------------------------------------------------------------
    gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))

    # -------------------------------------------------------------------------
    # Initialize loop variable
    # -------------------------------------------------------------------------
    dist = [None]*len(df['geometry'])
    pproj = [None]*len(df['geometry'])
    err = [None]*len(df['geometry'])
    Sy = [None]*len(df['geometry'])
    Sx = [None]*len(df['geometry'])
    alpha = [None]*len(df['geometry'])

    # -------------------------------------------------------------------------
    # Mesure orthoigonal distance between POINT and the rail reference
    # -------------------------------------------------------------------------
    if track_type == 'foward':
        for index, row in df.iterrows():
            if not math.isnan(row['geometry'].x) \
                    or not math.isnan(row['geometry'].x):
                dist[index], err[index], pproj[index], \
                    Sy[index], Sx[index], alpha[index] \
                    = errors(row['stdLong'],
                             row['stdLat'],
                             row['geometry'], rail_forth)
        df['pproj'] = pproj
        df['err'] = err
        df['SyTram'] = Sy
        df['SxTram'] = Sx
        df['alpha'] = alpha
        df['dist'] = dist
        return df
    elif track_type == 'backward':
        for index, row in df.iterrows():
            if not math.isnan(row['geometry'].x) \
                    or not math.isnan(row['geometry'].x):
                dist[index], err[index], pproj[index], \
                    Sy[index], Sx[index], alpha[index] \
                    = errors(row['stdLong'],
                             row['stdLat'],
                             row['geometry'], rail_back)
        df['pproj'] = pproj
        df['err'] = err
        df['SyTram'] = Sy
        df['SxTram'] = Sx
        df['alpha'] = alpha
        df['dist'] = dist
        return df
    elif track_type == 'too small':
        df = []
        return df
    else:
        print('there is a problem')
