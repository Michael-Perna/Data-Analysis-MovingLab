#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Oct 11 2021.

@author: Michael.
"""

# Import modules
import iso8601
import pytz


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
        format '%Y-%m-%dT%H:%M:%S%fZ'.

    """
    _date_obj = iso8601.parse_date(date)
    _date_utc = _date_obj.astimezone(pytz.utc)
    _date_utc_zformat = _date_utc.strftime('%Y-%m-%dT%H:%M:%S%fZ')
    return _date_utc_zformat
