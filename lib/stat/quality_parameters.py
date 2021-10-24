#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 16:03:45 2021

@author: michael
"""
# Import standard modules
from tqdm import tqdm
import pandas as pd
import numpy as np


def continuity(df, time):
    failEvent = 1
    eventDuration = 0
    n = 0
    dT = pd.DataFrame(columns=['dT_Fail'])
    df = df.reset_index(drop=True)
    # Progress bar
    loop = tqdm(total=len(df.index), position=0, desc='Calculating MTBF')
    i = 0
    continuity = np.empty([len(df.index), 3])
    continuity[:] = np.nan

    start = False
    for index in df.index[:-1]:
        Ts = df.iloc[index, 0]
        delta = df['timestamp'].iloc[index+1] - df['timestamp'].iloc[index]
        if delta.seconds > 300 and start:  # This is considered as a new track event after 5 minutes of connection loss
            T = df.iloc[index+1, 0] - Ts
            continuity[i][0] = dT.mean()[0].seconds/T.seconds
            continuity[i][1] = T.seconds
            continuity[i][2] = dT.mean()[0].seconds
            i += 1
            Ts = df.iloc[index+1, 0]
            start = False
        if df['posMode'].iloc[index] != 'RTK fixed' or delta.seconds > 5:
            eventDuration += 1
            # Si la pèrte du fixe dure plus que dix seconde on considère
            # comme un événement de 'fail'
            if eventDuration >= 10:
                eventDuration = 0         # Reset count

            if failEvent == 1:
                # Keep trace f the time of the event
                Tstart = df.iloc[index, 0]
                failEvent += 1
            if failEvent == 2:
                start = True
                Tend = df.iloc[index, 0]
                dT.loc[n] = [Tend - Tstart]
                failEvent == 0          # Reset count of Fail Event
                Tstart = df.iloc[index, 0]  # Reset Start Time
                n += 1

        loop.update(1)
    T = df.iloc[index+1, 0] - Ts
    if T.seconds > 1:
        continuity[i][0] = dT.mean()[0].seconds/T.seconds
        continuity[i][1] = T.seconds
        continuity[i][2] = dT.mean()[0].seconds
    loop.close()

    return continuity


def posMode(time, df, df_nf, df_ag, df_dg, df_rf, df_rfl):
    # Calculate Statistic by Fix Type
    if 'dist' in df.columns:
        posMode = {
            'start': df['timestamp'].iloc[0],
            'end': df['timestamp'].iloc[-1],
            'T': df['timestamp'].iloc[-1]-df['timestamp'].iloc[0],
            'epochs': len(df),

            'median': df['dist'].median(),
            'mean': df['dist'].mean(),
            'std': df['dist'].std(),

            # RTK Fix
            'RTK_Fix': len(df_rf) / time['epochsNotnan'],
            'median1': df_rf['dist'].median(),
            'mean1': df_rf['dist'].mean(),
            'std1': df_rf['dist'].std(),

            # RTK Float
            'RTK_Float': len(df_rfl) / time['epochsNotnan'],
            'median2': df_rfl['dist'].median(),
            'mean2': df_rfl['dist'].mean(),
            'std2': df_rfl['dist'].std(),

            # Differential GNSS fix
            'DGNSS_Fix': len(df_dg) / time['epochsNotnan'],
            'median3': df_dg['dist'].median(),
            'mean3': df_dg['dist'].mean(),
            'std3': df_dg['dist'].std(),

            # Differential GNSS fix
            'DGNSS_Auto': len(df_ag) / time['epochsNotnan'],
            'median4': df_ag['dist'].median(),
            'mean4': df_ag['dist'].mean(),
            'std4': df_ag['dist'].std(),

            # no fix
            'No_Fix': len(df_nf) / time['epochsNotnan'],

            # No position
            'No_Pos': (time['epochsNotnan']-len(df_rf)-len(df_rfl)-len(df_dg)-len(df_ag)-len(df_nf)) / time['epochsNotnan']
        }
    return posMode


def posDist(time, df, df10, df25, df50, df100, df500, dfinf):
    # Calculate Statistic by Fix Type
    if 'dist' in df.columns:
        posDist = {

            '10cm': len(df10) / time['epochsNotnan'],
            '20cm': len(df25) / time['epochsNotnan'],
            '50cm': len(df50) / time['epochsNotnan'],
            '100cm': len(df100) / time['epochsNotnan'],
            '500cm': len(df500) / time['epochsNotnan'],
            'inf': len(dfinf) / time['epochsNotnan']
        }
    return posDist


def posInteg(df_rf):

    df_rf_wrong = df_rf[(df_rf['dist'] > 0.5)]
    df_rf_wrong1 = df_rf[(df_rf['dist'] > 1)]
    df_rf_wrong2 = df_rf[(df_rf['dist'] > 2)]

    # Replace NaN HDOP with 1000
    df_rf_wrong.HDOP.fillna(10000, inplace=True)
    df_rf_wrong1.HDOP.fillna(10000, inplace=True)
    df_rf_wrong2.HDOP.fillna(10000, inplace=True)

    p50 = len(df_rf_wrong)/len(df_rf)
    p100 = len(df_rf_wrong1)/len(df_rf)
    p200 = len(df_rf_wrong2)/len(df_rf)

    corrHDOP_50 = np.corrcoef(
        df_rf_wrong.HDOP, df_rf_wrong.dist)       # No
    corrNumSV_50 = np.corrcoef(
        df_rf_wrong.numSV, df_rf_wrong.dist)     # Sligltly negative for Net -12%
    corrDifAge_50 = np.corrcoef(
        df_rf_wrong.difAge, df_rf_wrong.dist)   # No

    corrHDOP_200 = np.corrcoef(
        df_rf_wrong2.HDOP, df_rf_wrong2.dist)       # No
    corrNumSV_200 = np.corrcoef(
        df_rf_wrong2.numSV, df_rf_wrong2.dist)     # Sligltly negative for Net -12%
    corrDifAge_200 = np.corrcoef(
        df_rf_wrong2.difAge, df_rf_wrong2.dist)   # No

    corrHDOP_100 = np.corrcoef(
        df_rf_wrong1.HDOP, df_rf_wrong1.dist)       # No
    corrNumSV_100 = np.corrcoef(
        df_rf_wrong1.numSV, df_rf_wrong1.dist)     # Sligltly negative for Net -12%
    corrDifAge_100 = np.corrcoef(
        df_rf_wrong1.difAge, df_rf_wrong1.dist)   # No

    dist, bins, weights, CDF, quantile = _pdf_cdf(df_rf)

    integrity = {

        'dist': dist,
        'bins': bins,
        'weights': weights,
        'CDF': CDF,
        'quantile': quantile,
        'elem'
        'corrHDOP_50': corrHDOP_50,
        'corrNumSV_50': corrNumSV_50,
        'corrDifAge_50': corrDifAge_50,
        'p50': p50,
        'p100': p100,
        'p200': p200,
        'corrHDOP_100': corrHDOP_100,
        'corrNumSV_100': corrNumSV_100,
        'corrDifAge_100': corrDifAge_100,
        'corrHDOP_200': corrHDOP_200,
        'corrNumSV_200': corrNumSV_200,
        'corrDifAge_200': corrDifAge_200
    }
    return integrity
