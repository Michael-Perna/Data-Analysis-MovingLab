#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Oct 11 2021.

@author: Michael.
"""
import geopandas as gpd
import math
import fiona


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
