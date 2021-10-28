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


def distance_pt2shpline(point, polyline, point_proj=False):
    """
    Calculate shorter distance between point and polyline.

    Parameters
    ----------
    point : POINT tuple
        geographic coordinates: POINT(lat,lon)
    polyline : MULTILINE
        Description of a shapefile line, Muliple list containg POINT tuple
        which they represent the line.
    point_proj : bool, OPTIONAL
        If set as TRUE it return the projecet point  on the polylline

    Returns
    -------
    d : float
        shorter distance between the 'point' and the 'polyline'.
    pp: float
        projected point on the line.

    """
    d = 90000
    for line in polyline['geometry']:
        d_new = line.distance(point)
        if point_proj:
            pp_new = line.project(point)
        if d_new < d:
            d = d_new
            if point_proj:
                pp = pp_new
    if point_proj:
        pp = line.interpolate(pp)
        return d, pp
    else:
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


def _degmin2deg(degmin: float):
    """Transform string containig degree minutes data into float degree."""
    # TODO: make it vectorize
    a, b = str(degmin).split('.')
    d = int(a[:-2])
    m = float(a[-2:] + '.' + b)

    degrees = d + m/60
    return degrees


def _chrf95_to_itrf14_drift(df: object, index: str):
    """
    Apply Linear Interpolation to get drift between CHRF95 and ITRF14.

    Description
    -----------
    Apply linear interpolation between two months calculated
    drift to get an drift values for the day. The drift is needed
    to change the coor. ref. system from ITRF2014 at the current
    epoch to the CHRF95.

    Parameters
    ----------
    df : object
        DESCRIPTION.
    index : str
        DESCRIPTION.

    Returns
    -------
    dx : TYPE
        DESCRIPTION.
    dy : TYPE
        DESCRIPTION.
    dz : TYPE
        DESCRIPTION.

    """
    t = df.iloc[index, df.columns.get_loc('timestamp')] - _drift['epoch'][0]

    t = t.days
    dx = np.interp(t, _tp, _fx)
    dy = np.interp(t, _tp, _fy)
    dz = np.interp(t, _tp, _fz)
    return dx, dy, dz


def sum_std_pt(df: object, llh: list, index: int, stdLong='stdLong',
               stdLat='stdLat', stdAlt='stdAlt'):
    """Get llh coordinates of point plus std.

    Description
    -----------
    The standardt deviation are expressed in cartesian coordinates.

    Parameters
    ----------
    df : object
        dataframe containing the standardt deviations.
    llh : list
        Conatin longitude, latitude and altitude coor. of the points.
    index : int
        index of the dataframe row to sum.
    stdLong : str, optional
        Column name of teh Laltitude standard deviation.
        The default is 'stdLong'.
    stdLat : str, optional
        Column name of teh Laltitude standard deviation.
        The default is 'stdLat'.
    stdAlt : str, optional
        Column name of teh altitude standard deviation.
        The default is 'stdAlt'.

    Returns
    -------
    llh : list
        Point coordinates plus the standard deviation (longitute, latitude and
       altitute).

    """
    # -------------------------------------------------------------------------
    # Dataframe to matrix : Standr-deviation in WGS84
    # -------------------------------------------------------------------------
    Slon = pd.DataFrame(df[stdLong]).to_numpy()
    Slat = pd.DataFrame(df[stdLat]).to_numpy()
    Salt = pd.DataFrame(df[stdAlt]).to_numpy()

    # -------------------------------------------------------------------------
    # Convert in radiant for the llh2xyz function
    # -------------------------------------------------------------------------
    r_llh = np.array([None, None, llh[2]])
    r_llh[0] = np.pi / 180 * llh[0]
    r_llh[1] = np.pi / 180 * llh[1]

    # -------------------------------------------------------------------------
    # Transform geodesic coordinates to cartesian coordinates
    # -------------------------------------------------------------------------
    # Meausured point
    xyz1 = swiss_projection.llh2xyz(r_llh, 'WGS84')

    # Standartd Deviation of the measured point
    xyz2 = [Slon[index].tolist()[0],
            Slat[index].tolist()[0],
            Salt[index].tolist()[0]]

    # -------------------------------------------------------------------------
    # Geographic coordinates of the POINT + STD
    # -------------------------------------------------------------------------
    # Sum measured pont and standartd deviation
    xyz = [xyz2[0] + xyz1[0], xyz2[1] + xyz1[1], xyz2[2] + xyz1[2]]

    # Trasnform from cartestian to llh coordinates
    llh = swiss_projection.xyz2llh(xyz, 'WGS84')

    # Transform in degrees
    llh[0] = 180 / np.pi * llh[0]
    llh[1] = 180 / np.pi * llh[1]

    return llh


def mn95_projection(df: object, longitude='lon', latitude='lat',
                    altitude='alt', degmin=False, itrf14=False,
                    std=False, stdLong='stdLong', stdLat='stdLat',
                    stdAlt='stdAlt'):
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
    std: boolean
        If you want to also project the standardt deviation set std=True.
        The defeault value is False.
    stdLong : str, optional
        Column name of teh Laltitude standard deviation.
        The default is 'stdLong'.
    stdLat : str, optional
        Column name of teh Laltitude standard deviation.
        The default is 'stdLat'.
    stdAlt : str, optional
        Column name of teh altitude standard deviation.
        The default is 'stdAlt'.

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
            dx, dy, dz = _chrf95_to_itrf14_drift(df, index=index)

            # projection
            enh = swiss_projection.wgs84_itrf14_to_lv95(llh, [dx, dy, dz])
            df.iloc[index, [df.columns.get_loc(c)
                            for c in [longitude, latitude, altitude]]]\
                = enh

            if std:
                # -------------------------------------------------------------
                # Converstion to lv95 of the standard deviations
                # -------------------------------------------------------------
                llh1 = sum_std_pt(df, llh, index)

                enh1 = swiss_projection.wgs84_itrf14_to_lv95(llh1,
                                                             [dx, dy, dz])

                df.iloc[index, [df.columns.get_loc(c)
                                for c in [stdLong, stdLat, stdAlt]]]\
                    = [abs(round(enh[0] - enh1[0], 5)),
                       abs(round(enh[1] - enh1[1], 5)),
                       abs(round(enh[2] - enh1[2], 5))]
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
            enh = swiss_projection.wgs84_to_lv95(llh)
            df.iloc[index, [df.columns.get_loc(c)
                            for c in [longitude, latitude, altitude]]]\
                = enh

            if std:
                # -------------------------------------------------------------
                # Converstion to lv95 of the standard deviations
                # -------------------------------------------------------------
                llh1 = sum_std_pt(df, llh, index)

                enh1 = swiss_projection.wgs84_to_lv95(llh1)

                df.iloc[index, [df.columns.get_loc(c)
                                for c in [stdLong, stdLat, stdAlt]]]\
                    = [abs(round(enh[0] - enh1[0], 5)),
                       abs(round(enh[1] - enh1[1], 5)),
                       abs(round(enh[2] - enh1[2], 5))]
            # Progress bar:
            loop.update(1)
        loop.close()
        return df
