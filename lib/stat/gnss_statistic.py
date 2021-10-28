#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Sun Oct 24 13:56:01 2021.

@author: michael
"""

# Import standart module
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import shapefile

# Import local modules
from lib import plot
from lib import stat
from lib import global_
from lib import input_


class Statistic:
    def __init__(self, df, receiver):

        self.receiver = receiver
        self.rail_f = shapefile.Reader(input_.rail_forth)
        self.rail_b = shapefile.Reader(input_.rail_back)

        # ---------------------------------------------------------------------
        # Set Timestamp as dataframe index
        # ---------------------------------------------------------------------
        # df = df.set_index(pd.to_datetime(df['timestamp']))

        # ---------------------------------------------------------------------
        # CLEAN DATA FROM DATA OUT OF REFERENCE
        # ---------------------------------------------------------------------
        for bad_day in global_.bad_days:
            df = df.drop(df.loc[bad_day].index)

        # ---------------------------------------------------------------------
        # Time Statistic
        # ---------------------------------------------------------------------
        print('Get time statistic')
        # Time statistics
        self.time = {'start': df['timestamp'].iloc[0],
                     'end': df['timestamp'].iloc[-1],
                     'T': df['timestamp'].iloc[-1]-df['timestamp'].iloc[0],
                     'epochs': len(df),
                     'epochsNotnan': len(df[~np.isnan(df.lon)])
                     }

        # ---------------------------------------------------------------------
        # CLASSIFY ACCORDINGLY POTITION MODE
        # ---------------------------------------------------------------------
        self.df_nf = df[df['posMode'] == 'No fix']                 # No fix
        # Autonomous GNSS fix
        self.df_ag = df[df['posMode'] == 'Autonomous GNSS fix']
        # Differential GNSS fix
        self.df_dg = df[df['posMode'] == 'Differential GNSS fix']
        self.df_rf = df[df['posMode'] == 'RTK fixed']              # RTK fixed
        self.df_rfl = df[df['posMode'] == 'RTK float']             # RTK float
        # all position which are not RTK fixed
        self.df_nrf = df[df['posMode'] != 'RTK fixed']

        # ---------------------------------------------------------------------
        # CLASSIFY ACCORDINGLY pRECISION
        # ---------------------------------------------------------------------
        self.df10 = df[(df['dist'] <= 0.10)]
        self.df25 = df[(df['dist'] > 0.10) & (df['dist'] <= 0.25)]
        self.df50 = df[(df['dist'] > 0.25) & (df['dist'] <= 0.50)]
        self.df100 = df[(df['dist'] > 0.50) & (df['dist'] <= 1)]
        self.df500 = df[(df['dist'] > 1) & (df['dist'] <= 5)]
        self.dfinf = df[(df['dist'] > 5)]

    def plt_bad_days(self, df: object, days: list):
        """Scatter plot with the point of the day."""
        fig, ax = plt.subplots()
        for day in days:
            # ax.scatter(df.lon, df.lat)
            ax.scatter(df.loc[day].lon, df.loc[day].lat, label=day)
        for shape in self.rail_b.shapeRecords():
            x = [i[0] for i in shape.shape.points[:]]
            y = [i[1] for i in shape.shape.points[:]]
            ax.plot(x, y)
        for shape in self.rail_f.shapeRecords():
            x = [i[0] for i in shape.shape.points[:]]
            y = [i[1] for i in shape.shape.points[:]]
            ax.plot(x, y)
        ax.legend()
        return

    def rmv_bad_days(self, df):
        """Ignore days where the tram took paths outside the reference."""
        for bad_day in global_.bad_days:
            df = df.drop(df.loc[bad_day].index)
        return df

    def integrity(self, df):
        """Meausre integrity of df."""
        integrity = stat.posInteg(df)
        return integrity

    def accuracy(self, df, do_plot, do_xlim=True):
        """Calculate accuracy of df."""
        # Probability Density Function PDF
        dist, bins, weights, CDF, quantile = stat.pdf_cdf(df)
        # Plot Accuracy Histogram
        if do_plot:
            print('Plot Accuracy Distance')
            plot.plotHistAcc(dist, bins, weights, CDF, quantile, self.receiver,
                             do_xlim=True)
        return quantile

    def continuity(self, df):
        """Calculate continuity of df."""
        print('Estimating Continuity')
        continuity = stat.continuity(df, self.time)
        cont = continuity[:, 0][~np.isnan(continuity[:, 0])]
        continuity = np.average(cont)
        return continuity

    def disponibility(self):
        """Calculate disponobility of the different category."""
        print('Estimating disponibility')
        posMode = stat.posMode(self.time, self.df_rf, self.df_nf, self.df_ag,
                               self.df_dg, self.df_rf, self.df_rfl)
        posDist = stat.posDist(self.time, self.df, self.df10, self.df25,
                               self.df50, self.df100, self.df500, self.dfinf)
        return posMode, posDist

    def spatial_analysis(self, df, lateral_err):
        """Do simple spatial Analysis."""
        df = df[(df['dist'] > lateral_err)]
        fig, ax = plt.subplots()
        df.reset_index(drop=True)
        ax.scatter(df.lon, df.lat)

        for shape in self.rail_b.shapeRecords():
            x = [i[0] for i in shape.shape.points[:]]
            y = [i[1] for i in shape.shape.points[:]]
            ax.plot(x, y)
        for shape in self.rail_f.shapeRecords():
            x = [i[0] for i in shape.shape.points[:]]
            y = [i[1] for i in shape.shape.points[:]]
            ax.plot(x, y)

        fig, ax = plt.subplots()
        df.reset_index(drop=True)
        ax.plot(range(len(df.dist)), df.dist)
