#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 10:07:43 2021.

@author: michael
"""


# Import local modules
from lib import input_

# Import standard module
import geopandas as gpd
import warnings
from geopandas.tools import sjoin

warnings.simplefilter(action='ignore')


def rmv_unsafe_points(df: object, shp_file=input_.loop_shp):
    """
    Remove points containted by shp_file.

    Description
    -----------
    The tram when is in loops or bus station with multiple
    tram platform it is not possible for the algorith to predict
    in which rails the tram will be. Therefore I cannot apply
    right reference and I remove those region. Morover the tram
    continue to get GPS signals inside the depôt which is near the
    railsway and it polluate the results.

    Parameters
    ----------
    df : object
        Dataframe containg all receiver's point meausurements.
    shp_file: str
        shape file containing unsafe area for the gnss analysis.
        Defeault values: input_.loop_shp.

    Returns
    -------
    df3 : TYPE
        Dataframe containg only points inside the input_.loop_shp.
    """
    # ----------------------------------------------------------------
    # Remove meausures insde unsafe and biased area
    # ----------------------------------------------------------------

    # Remove NaN longitude and latitude for the gpd function
    df2 = df[df['lon'].notna()]  # df without NaN
    df1 = df[df['lon'].isna()]  # df wih only Nan

    # Transform lon, lan point to shapefile points
    points = gpd.GeoDataFrame(df2, geometry=gpd.points_from_xy(df2.lon,
                                                               df2.lat))
    pointFrame = gpd.GeoDataFrame(geometry=gpd.GeoSeries(points.geometry))

    # Upload unsafe area shapefile
    poly = gpd.GeoDataFrame.from_file(shp_file)

    # Join Both shapefile
    pointInPolys = sjoin(pointFrame, poly, how='left')

    # Remove index with duplicate values
    if not pointInPolys.index.is_unique:
        pointInPolys.index.duplicated()
        pointInPolys = pointInPolys.loc[~pointInPolys.index.duplicated(), :]

    # Keep only point outside the join
    df2 = df2[pointInPolys.id.isnull()]

    # Merge to the entire df to preserve epochs without position
    df3 = df2.append(df1)

    # Limit distance to mm to save memory space
    df3['dist'] = df3['dist'].round(3)

    return df3


def select_zone(df: object, zone: str):
    """
    Remove all points outside the zone shapefile.

    Parameters
    ----------
    df : object
        Dataframe containg all receiver's point meausurements.
    zone : str
        shape file containing the area to analysis.

    Returns
    -------
    df3 : TYPE
        Dataframe containg only point meausurements inside the zone.

    """
    # Remove NaN longitude and latitude for the gpd function
    df2 = df[df['lon'].notna()]  # df without NaN
    df1 = df[df['lon'].isna()]  # df wih only Nan

    # Transform lon, lan point to shapefile points
    points = gpd.GeoDataFrame(df2, geometry=gpd.points_from_xy(df2.lon,
                                                               df2.lat))
    pointFrame = gpd.GeoDataFrame(geometry=gpd.GeoSeries(points.geometry))

    # Upload unsafe area shapefile
    poly = gpd.GeoDataFrame.from_file(zone)

    # Join Both shapefile
    pointInPolys = sjoin(pointFrame, poly, how='left')

    # Remove index with duplicate values
    if not pointInPolys.index.is_unique:
        pointInPolys.index.duplicated()
        pointInPolys = pointInPolys.loc[~pointInPolys.index.duplicated(), :]

    # Keep only point outside the join
    df2 = df2[~pointInPolys.id.isnull()]

    # Merge to the entire df to preserve epochs without position
    df3 = df2.append(df1)

    return df3
