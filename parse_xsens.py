#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 13:30:51 2021.

@author: Michael
"""

import pandas as pd
import os
import iso8601
import pytz


class ParseXsens:
    """Parse x-sens data into .SNMEA format."""

    def __init__(self, txt_file, save):
        self.txt_file = txt_file
        self.save = save

        # Create Data Frame
        columns = ['timestamp', 'lon', 'stdLong', 'lat', 'stdLat', 'alt',
                   'stdAlt', 'sep', 'rangeRMS', 'posMode', 'numSV',
                   'difAge', 'numGP', 'numGL', 'numGA', 'numGB',
                   'opMode', 'navMode',
                   'PDOP', 'HDOP', 'VDOP', 'stdMajor', 'stdMinor', 'orient',
                   'fixType']

        self.df_out = pd.DataFrame(
            data=None, index=None, columns=columns, dtype=None, copy=False)

    def utcrcf3339(self, date: str):
        """Convert UTC time string into UTC Z format '%Y-%m-%dT%H:%M:%SZ'."""
        _date_obj = iso8601.parse_date(date)
        _date_utc = _date_obj.astimezone(pytz.utc)
        _date_utc_zformat = _date_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        return _date_utc_zformat

    def main(self):
        """
        Write a .SNMEA file containig the parsed data.

        Parameters
        ----------
        self.txt_file : text file
                        Text file that contain the xsens data


        Returns
        -------
        df : pandas dataframe
            Dataframe containing the parsed data of the xsens.

        """
        # Open txt file
        print('loading : ', self.txt_file)
        df = pd.read_csv(self.txt_file, dtype=str)

        # Date
        df['date'] = df['UTC_Year'] + df['UTC_Month'].str.zfill(2) +\
            df['UTC_Day'].str.zfill(2) + 'T' + \
            df['UTC_Hour'].str.zfill(2) +\
            df['UTC_Minute'].str.zfill(2) + df['UTC_Second']

        df['timestamp'] = df['date'].map(lambda x: self.utcrcf3339(x))

        # Fill output
        self.df_out['timestamp'] = df['timestamp']
        self.df_out['lon'] = df['Longitude']
        self.df_out['lat'] = df['Latitude']
        self.df_out['alt'] = df['Altitude']
        self.df_out['numSV'] = df['NumberOfSV']
        self.df_out['fixType'] = df['GNSSFixtype']
        self.df_out['PDOP'] = df['PositionDOP']
        self.df_out['HDOP'] = df['HorizontalDOP']
        self.df_out['VDOP'] = df['VerticalDOP']

        # Save as .SNMEA
        # --------------
        if self.save:
            head, tail = os.path.split(self.txt_file)
            root, ext = os.path.splitext(tail)

            # save the entire dataframe as a csv file
            print('saving : ' + head + '/snmea/' + root + ".snmea")
            self.df_out.to_csv(head + '/snmea/' + root + ".snmea")

        return df


# Manually isn't nice but effective
# mars = ParseXsens('./data/18_03_2021/xsens_00.txt')
# df = mars.main()

# mars = ParseXsens('./data/18_03_2021/xsens_01.txt')
# df = mars.main()

# mars = ParseXsens('./data/18_03_2021/xsens_02.txt')
# df = mars.main()

# mars = ParseXsens('./data/18_03_2021/xsens_03.txt')
# df = mars.main()

# mars = ParseXsens('./data/18_03_2021/xsens_04.txt')
# df = mars.main()

# mars = ParseXsens('./data/18_03_2021/xsens_05.txt')
# df = mars.main()

# mars = ParseXsens('./data/18_03_2021/xsens_06.txt')
# df = mars.main()

# mars = ParseXsens('./data/18_03_2021/xsens_07.txt')
# df = mars.main()

# mars = ParseXsens('./data/18_03_2021/xsens_08.txt')
# df = mars.main()

# mars = ParseXsens('./data/18_03_2021/xsens_09.txt')
# df = mars.main()

# mars = ParseXsens('./data/18_03_2021/xsens_10.txt')
# df = mars.main()