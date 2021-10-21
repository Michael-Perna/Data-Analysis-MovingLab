#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Oct 11 2021.

@author: Michael.
"""

# Import modules
import iso8601
import pytz
import pandas as pd


def utcrcf3339(date: str):
    """
    Change UTC time format to the UTC RCF3339 Standar.

    Parameters
    ----------
    date : str
        utc time string.

    Returns
    -------
    _date_utc_zformat : str
        format '%Y-%m-%dT%H:%M:%S.%fZ'.

    """
    _date_obj = iso8601.parse_date(date)
    _date_utc = _date_obj.astimezone(pytz.utc)
    _date_utc_zformat = _date_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return _date_utc_zformat


def sync(df1, df2, time_format1: str, time_format2: str):
    # BUG: This function could not work as epected
    """
    Synchronize df1 and df2 with geopandas.align function.

    Description
    -----------
    Synchronize df1 & df2 dataframe which are 2 distinct meausures of the
    two theodolites of the same surveys (during the same time span).

    Parameters
    ----------
    df1 : dataframe
        Survey of the first thetolite, it must have a 'timestamp' column.
    df2 : dataframe
        Survey of the first thetolite, it must have a 'timestamp' column.
    time_format1 : str
        String that describe the format of the timestamp column in df1.
    time_format2 : str
        String that describe the format of the timestamp column in df1.


    Returns
    -------
    df1 : dataframe
        Synchronized survey of the first thetolite.
    df2 : dataframe
        Synchronized survey of the first thetolite.

    """
    # Sort data by ascending time
    df1 = df1.sort_values(by=['timestamp'])
    df2 = df2.sort_values(by=['timestamp'])

    # Transform time string to time format for max/min function use
    df1['timestamp'] = pd.to_datetime(df1['timestamp'],
                                      format=time_format1)
    df2['timestamp'] = pd.to_datetime(df2['timestamp'],
                                      format=time_format2)

    # Found minimum overlapping time
    _tmin1 = df1['timestamp'].min()
    _tmax1 = df1['timestamp'].max()
    _tmin2 = df2['timestamp'].min()
    _tmax2 = df2['timestamp'].max()

    _tmin = max(_tmin1, _tmin2)  # /!\ time min/max are inverted
    _tmax = min(_tmax1, _tmax2)  # /!\ time min/max are inverted

    # Get just timelaps that are present in both series
    df1 = df1[(df1['timestamp'] > _tmin) & (df1['timestamp'] < _tmax)]
    df2 = df2[(df2['timestamp'] > _tmin) & (df2['timestamp'] < _tmax)]

    # Synchronize the dataframe
    # FIXME: df1 and df2 are the same
    df1, df2 = df1.align(df2)
    return df1
