#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Oct 11 2021.

@author: Michael.
"""

# Standard packages
from tqdm import tqdm

import geopandas as gpd
import pandas as pd
import numpy as np
import math
import fiona


# Local variables
from .swissprojection import swiss_projection

# Global variables
from lib import global_

# Local variables

# Shift CHTRF95 – ITRF2014 for each month in the year 2021
_drift = global_.drift2021
_drift = pd.DataFrame(_drift, columns=['epoch', 'dx', 'dy', 'dz'])
_drift['epoch'] = pd.to_datetime(_drift.epoch, format='%Y-%m-%d')
_drift['t'] = _drift['epoch'] - _drift['epoch'][0]
_tp = _drift.t.dt.days.astype(int).to_numpy()
_fx = _drift.dx.to_numpy()
_fy = _drift.dy.to_numpy()
_fz = _drift.dz.to_numpy()


def _degmin2deg(degmin: float):
    """Transform string containig degree minutes data into float degree."""
    # TODO: make it vectorize
    a, b = str(degmin).split('.')
    d = int(a[:-2])
    m = float(a[-2:] + '.' + b)

    degrees = d + m/60
    return degrees


def _mn95_to_itrf14_drift(df: object, index: str):
    t = df.iloc[index, df.columns.get_loc('timestamp')] - _drift['epoch'][0]

    t = t.days
    dx = np.interp(t, _tp, _fx)
    dy = np.interp(t, _tp, _fy)
    dz = np.interp(t, _tp, _fz)
    return dx, dy, dz


def mn95_projection(df: object, longitude='lon', latitude='lat',
                    altitude='alt', degmin=False, itrf14=False):
    """
    Project CHTRF95 (WGS84) coordinates into MN95.

    Parameters
    ----------
    df : dataframe object
        Dataframe containg as column 'Longitude', 'latitude and 'altitude' in
        expressed CHTR95. Longitute and latitude are expressed in degree.
    longitude : str, optional
        Column name where the longitude coordinates are saved.
        The default is 'lon'.
    latitude : str, optional
        Column name where the latitude coordinates are saved.
        The default is 'lat'.
    altitude : str, optional
        Column name where the altitude coordinates are saved.
        The default is 'alt'.
    degmin : boolean
        If the longitude and latitude coordinates are in degree minutes set
        degmin=True.
        The defeault value is False.
    itrf14 : boolean
        If the longitude and latitude coordinates are in the ITRF14 set
        itrf14=True.
        The defeault value is False.

    Returns
    -------
    df : dataframe object
        Dataframe with the transformed coordinates in MN95.

    """
    # -------------------------------------------------------------------------
    # Convert in degree (nmea format)
    # -------------------------------------------------------------------------
    if degmin:
        # FIXME: Warning message :df
        # A value is trying to be set on a copy of a slice from a DataFrame.
        df[longitude] = df[longitude].map(lambda x: _degmin2deg(x))
        df[latitude] = df[latitude].map(lambda x: _degmin2deg(x))
    # -------------------------------------------------------------------------
    # Dataframe to matrix
    # -------------------------------------------------------------------------
    lon = pd.DataFrame(df[longitude]).to_numpy()
    lat = pd.DataFrame(df[latitude]).to_numpy()
    alt = pd.DataFrame(df[altitude]).to_numpy()

    # -------------------------------------------------------------------------
    # Converstion to lv95
    # -------------------------------------------------------------------------
    if itrf14:
        # Converstion from itrf14 to lv95
        # Progress bar
        loop = tqdm(total=len(alt), desc='Coordinates transformation ..',
                    position=0, leave=False)

        for index in range(len(alt)):
            # llh vector
            llh = [lon[index].tolist()[0],
                   lat[index].tolist()[0],
                   alt[index].tolist()[0]]
            # Estimate drift between mn95 and itrf14
            dx, dy, dz = _mn95_to_itrf14_drift(df, index=index)

            # projection
            df.iloc[index, [df.columns.get_loc(c)
                            for c in [longitude, latitude, altitude]]]\
                = swiss_projection.wgs84_itrf14_to_lv95(llh, [dx, dy, dz])
            # Progress bar:
            loop.update(1)
        loop.close()
        return df

    else:
        # Converstion from chrf95 to lv95
        # Progress bar
        loop = tqdm(total=len(alt), desc='Coordinates transformation ..',
                    position=0, leave=False)
        for index in range(len(alt)):
            # llh vector
            llh = [lon[index].tolist()[0],
                   lat[index].tolist()[0],
                   alt[index].tolist()[0]]
            # conversion
            df.iloc[index, [df.columns.get_loc(c)
                            for c in [longitude, latitude, altitude]]]\
                = swiss_projection.wgs84_to_lv95(llh)
            # Progress bar:
            loop.update(1)
        loop.close()
        return df


def distance_pt2shpline(point, polyline):
    """
    Calculate shorter distance between point and polyline.

    Parameters
    ----------
    point : POINT tuple
        geographic coordinates: POINT(lat,lon)
    polyline : MULTILINE
        Description of a shapefile line, Muliple list containg POINT tuple
        which they represent the line.

    Returns
    -------
    d : float
        shorter distance between the 'point' and the 'polyline'.

    """
    d = 90000
    for line in polyline['geometry']:
        d_new = line.distance(point)
        if d_new < d:
            d = d_new
    return d


def distance_df2shpfile(df, x: str, y: str, shpfile: str):
    """
    Calculate shorter distance between a point (x, y) and a shape LINE.

    Parameters
    ----------
    df : dataframe
        dataframe containng x and y.
    x:  str
        name of the column containg longitude values
    y:  str
        name of the column containg latitude values
    shpfile : str
        Name of the shapefile folder contaiing the shapeline.

    Returns
    -------
    df : dataframe
        containing the distance between POINT and shpfile LINE for each POINT.

    """
    # Load rails als shapefile
    rail_forth = gpd.read_file(shpfile)

    # East/North to gpd points geometry
    gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[x], df[y]))

    # Mesure distance from the rail
    dist = [None]*len(df['geometry'])

    for index, row in df.iterrows():
        if not math.isnan(row['geometry'].x) \
                or not math.isnan(row['geometry'].x):
            dist[index] = distance_pt2shpline(row['geometry'], rail_forth)
    df['dist'] = dist

    return df


def pt2shpline(df, shpfile_out: str):
    """
    Make a shapefile line from list of point.

    Parameters
    ----------
    shpfile_out : str
        Name of the output shapefile.
    df : dataframe
        dataframe containing the points needed to create the line.

    Returns
    -------
    lineShp : LINE
        Shapefile line.

    """
    # define shapefile schema
    schema = {
        'geometry': 'LineString',
        'properties': [('Name', 'str')]
    }

    # open a fiona object
    lineShp = fiona.open(shpfile_out, mode='w', driver='ESRI Shapefile',
                         schema=schema)

    # Remove NaN coordinates
    df = df[~df['lon'].isna()].reset_index()
    df = df[~df['lat'].isna()].reset_index()

    # get list of points
    xyList = []
    rowTime = ''
    for index, row in df.iterrows():
        xyList.append((row.lon, row.lat))
        rowTime = row.timestamp

    # save record and close shapefile
    rowDict = {
        'geometry': {'type': 'LineString',
                     'coordinates': xyList},
        'properties': {'Name': rowTime},
    }

    lineShp.write(rowDict)

    # close fiona object
    lineShp.close()

    return lineShp
