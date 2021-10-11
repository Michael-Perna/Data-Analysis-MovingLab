# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 12:54:01 2021.

@author: Michael
"""
import pandas as pd
import geopandas as gpd
from lib.plot_theo import plotHistDist, plotHistDist2, plotHist, plotHist2
from lib.plot_theo import plotShpLine, plotRefLine
from lib import geotools
from lib import timetools


class ParseTheo:
    """Parse and Measure distance on the thodolites data."""

    def __init__(self, txt_file: str, shpfile: str):
        self.txt_file = txt_file
        self.shpfile = shpfile

        # Create Data Frame
        columns = ['timestamp', 'lon', 'stdLong', 'lat', 'stdLat', 'alt',
                   'stdAlt', 'sep', 'rangeRMS', 'posMode', 'numSV',
                   'difAge', 'numGP', 'numGL', 'numGA', 'numGB',
                   'opMode', 'navMode',
                   'PDOP', 'HDOP', 'VDOP', 'stdMajor', 'stdMinor', 'orient',
                   'fixType']

        self.df_out = pd.DataFrame(
            data=None, index=None, columns=columns, dtype=None, copy=False)

    def main(self):
        """
        Import data and meausre the distance with the reference.

        Returns
        -------
        self.df_output : dataframe
            dataframe containg the original dataframe plus the distances
            results
        """
        # Open txt file
        df = pd.read_csv(self.txt_file, sep='\t', skiprows=[1],
                         encoding='unicode_escape', dtype=str)

        # Convert UTC date into utcrcf3339 standard
        df['date'] = df['Year'] + df['Month'].str.zfill(2) +\
            df['Day'].str.zfill(2) + 'T' + \
            df['Hour'].str.zfill(2) +\
            df['Minute'].str.zfill(2) + df['Second']

        df['timestamp'] = df['date'].map(lambda x: timetools.utcrcf3339(x))

        df = geotools.distance_df2shpfile(df, shpfile=self.shpfile,
                                          x='East', y='North')

        # Fill output
        self.df_out['timestamp'] = df['timestamp']
        self.df_out['lon'] = df['East'].astype(float)
        self.df_out['lat'] = df['North'].astype(float)
        self.df_out['alt'] = df['Altitude'].astype(float)
        self.df_out['dist'] = df['dist']

        return self.df_out


class AnalysisTheo:
    """Analysis of the theotolites measures quality."""

    def __init__(self, df1, df2, shpFilePath: str, idx: str,
                 do_plot1: bool, do_plot2: bool):
        self.df1 = df1
        self.df2 = df2
        self.idx = idx
        self.do_plot1 = do_plot1
        self.do_plot2 = do_plot2
        self.shpFilePath = shpFilePath

    def timeorder(self, df):
        """Apply '%Y-%m-%dT%H:%M:%S%fZ' time format and sort it."""
        # Rearrange théodolites series
        # Transform time string to time format
        df['timestamp'] = pd.to_datetime(df['timestamp'],
                                         format='%Y-%m-%dT%H:%M:%S%fZ')

        # Sort data by ascending time
        df = df.sort_values(by=['timestamp'])
        return df

    def sync(self, df1, df2):
        """
        Synchronize df1 and df2 with geopandas.align function.

        Description
        -----------
        Synchronize df1 & df2 dataframe which are 2 distinct meausures of the
        two theodolites of the same surveys (during the same time span).

        Parameters
        ----------
        df1 : dataframe
            Survey of the first thetolite.
        df2 : dataframe
            Survey of the first thetolite.

        Returns
        -------
        df1 : dataframe
            Synchronized survey of the first thetolite.
        df2 : dataframe
            Synchronized survey of the first thetolite..

        """
        # Found minimum overlapping time
        tmin1 = df1['timestamp'].min()
        tmax1 = df1['timestamp'].max()
        tmin2 = df2['timestamp'].min()
        tmax2 = df2['timestamp'].max()

        tmin = max(tmin1, tmin2)  # /!\ time min/max are inverted
        tmax = min(tmax1, tmax2)  # /!\ time min/max are inverted

        # Get just timelaps that are present in both series
        df1 = df1[(df1['timestamp'] > tmin) & (df1['timestamp'] < tmax)]
        df2 = df2[(df2['timestamp'] > tmin) & (df2['timestamp'] < tmax)]

        # Synchronize the dataframe
        df1, df2 = df1.align(df2)
        return df1, df2

    def stat(self, df1, df2):
        """Compute basic statistic std & mean of the apprx. error."""
        # Statistics
        delta = df1['dist']-df2['dist']
        timedelta = df1['timestamp']-df2['timestamp']
        std = delta.std()
        mean = delta.mean()

        return delta, timedelta, std, mean

    def main(self):
        """Analyse the theodolite measures quality."""
        # Change time format and sortby timstamp
        self.df1 = self.timeorder(self.df1)
        self.df2 = self.timeorder(self.df2)

        # Synchronize the dataframe
        self.df1, self.df2 = self.sync(self.df1, self.df2)

        # Statistic
        delta, timedelta, std, mean = self.stat(self.df1, self.df2)

        # Remove values outside 2 times the std
        df1_new = self.df1[(self.df1['dist'] >= mean - std) &
                           (self.df1['dist'] <= mean + std)]
        df2_new = self.df2[(self.df2['dist'] >= mean - std) &
                           (self.df2['dist'] <= mean + std)]

        # Synchronize the dataframe
        df1_new, df2_new = self.sync(df1_new, df2_new)

        # Statistic
        delta_new, timedelta_new, std_new, mean_new = self.stat(df1_new,
                                                                df2_new)

        # plot
        if self.do_plot1:
            # PLOT Figure 1- Obs Brute
            plotHistDist(self.df1, self.df2, delta, self.shpFilePath, self.idx)
            plotHistDist2(self.df1, self.df2, delta, self.shpFilePath,
                          self.idx)
        if self.do_plot2:
            # PLOT Figure 1- Obs improved
            plotHistDist(df1_new, df2_new, delta_new, shpFilePath, self.idx)
            plotHistDist2(df1_new, df2_new, delta_new, shpFilePath, self.idx)

        # Prepare Class object output
        self.df1 = df1_new
        self.df2 = df2_new
        self.mean = mean_new
        self.std = std_new
        self.delta = delta_new
        self.timedelta = timedelta_new

        self.df1_old = self.df1
        self.df2_old = self.df2
        self.mean_old = mean
        self.std_old = std
        self.delta_old = delta
        self.timedelta_old = timedelta

        return self


class AnalysisTheo2:
    """Analyse the receiver precision in respect to the theodolite measures."""

    def __init__(self, df, df2, shpfile_out1, shpfile_out2, shpRailPath,
                 swipos_netr9, swps_blox, sapcorda):
        self.df = df
        self.df2 = df2
        self.shpfile_out1 = shpfile_out1
        self.shpfile_out2 = shpfile_out2
        self.shpRailPath = shpRailPath
        self.spws_ublox = swps_blox
        self.netr9 = swipos_netr9
        self.sapcorda = sapcorda

    def main(self):
        """Do the Analysis between the receiver and the theodolite."""
        theo1 = geotools.pt2shpline(self.shpfile_out1, self.df)
        theo2 = geotools.pt2shpline(self.shpfile_out2, self.df2)
        df_ubx = pd.read_csv(self.spws_ublox)
        df_sap = pd.read_csv(self.sapcorda)
        df_netr9 = pd.read_csv(self.netr9)

        # Plot
        plotRefLine(self.shpfile_out1, self.shpfile_out2, self.shpRailPath,
                    self.df, self.df2
                    )
        # plotShpLine(self.shpfile_out1, self.shpRailPath, self.df, df_netr9,
        # df_ubx,df_sap)
        return theo1, theo2
