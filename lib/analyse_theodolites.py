# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 12:54:01 2021.

@author: Michael
"""
import pandas as pd
import geopandas as gpd


from .plot import plotHistDist
from .plot import plotHistDist2
from .plot import plotHist
from .plot import plotHist2

from .plot import plotShpLine
from .plot import plotRefLine

from . import geolib
from . import timetools
from . import global_


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
        self.df1 = self.timeorder(self.df1)
        self.df2 = self.timeorder(self.df2)

        # Synchronize the dataframe
        self.df1, self.df2 = timetools.sync(self.df1, self.df2)

        # Statistic
        delta, timedelta, std, mean = self.stat(self.df1, self.df2)

        # Remove values outside 2 times the std
        df1_new = self.df1[(self.df1['dist'] >= mean - std) &
                           (self.df1['dist'] <= mean + std)]
        df2_new = self.df2[(self.df2['dist'] >= mean - std) &
                           (self.df2['dist'] <= mean + std)]

        # Synchronize the dataframe
        df1_new, df2_new = timetools.sync(df1_new, df2_new)

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
        theo1 = geolib.pt2shpline(self.shpfile_out1, self.df)
        theo2 = geolib.pt2shpline(self.shpfile_out2, self.df2)
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
