#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 11:27:00 2021.

@author: michael
"""
import matplotlib.pyplot as plt
import shapefile


def plot_trace(rail_shp_path: str, shp_path: str, receiver_name: str,
               df: object):
    """
    Plot the rail references as the receiver obs. and his trace.

    Parameters
    ----------
    rail_shp_path : str
        Path to the rail shape reference.
    shp_path : str
        Path to the trace of the receiver.
    receiver_name : str
        Name of the receiver.
    df : object
        Dataframe conting the receiver observation (lon, lat).

    Returns
    -------
    None.

    """
    # Load rails als shapefile
    shp = shapefile.Reader(shp_path)
    rail = shapefile.Reader(rail_shp_path)

    # PLot observations
    plt.scatter(df['lon'], df['lat'])

    for shape in shp.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y, label=receiver_name)

    for shape in rail.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y)

    # # Box / axis Limit
    # _xmin = df['lon'].min()-100
    # _xmax = df['lon'].max()+100
    # _ymin = df['lat'].min()-100
    # _ymax = df['lat'].max()+100

    # plt.xlim([_xmin, _xmax])
    # plt.ylim([_ymin, _ymax])
    plt.legend()
    plt.show()
