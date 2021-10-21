#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 11 11:31:51 2021.

@author: michael
"""
from lib import ParseTheo, AnalysisTheo, AnalysisTheo2


base = './data/'
shpFilePath = './maps/railways/foward_track_adjusted.shp'

# Get
t2a = ParseTheo(base + 'trajectoire_2_st1.txt', shpFilePath)
t2b = ParseTheo(base + 'trajectoire_2_st2.txt', shpFilePath)
t3a = ParseTheo(base + 'trajectoire_3_st1.txt', shpFilePath)
t3b = ParseTheo(base + 'trajectoire_3_st2.txt', shpFilePath)
t4a = ParseTheo(base + 'trajectoire_4_st1.txt', shpFilePath)
t4b = ParseTheo(base + 'trajectoire_4_st2.txt', shpFilePath)
t5a = ParseTheo(base + 'trajectoire_5_st1.txt', shpFilePath)
t5b = ParseTheo(base + 'trajectoire_5_st2.txt', shpFilePath)
df2a = t2a.main()
df2b = t2b.main()
df3a = t3a.main()
df3b = t3b.main()
df4a = t4a.main()
df4b = t4b.main()
df5a = t5a.main()
df5b = t5b.main()


# Analyse 2
track_file = './DataBase/2021/March/18/tracks/'
shp2a = base + 'line/' + 'trajectoire_2_st1' + ".shp"
shp2b = base + 'line/' + 'trajectoire_2_st2' + ".shp"
shp5a = base + 'line/' + 'trajectoire_5_st1' + ".shp"
shp5b = base + 'line/' + 'trajectoire_5_st2' + ".shp"
swipos_ublox = track_file + 'swipos_ublox.csv'
swipos_netr9 = track_file + 'swipos_NetR9-copy__10_30_10_11_10_48.result'
sapcorda = track_file + 'sapcorda.result'
# Analyse 1
do_plot0 = False
if do_plot0:
    plotHist(df2a['dist'], df2b['dist'], 2, df3a['dist'], df3b['dist'], 3)
    plotHist(df4a['dist'], df4b['dist'], 2, df5a['dist'], df5b['dist'], 3)

do_plot1 = True
do_plot2 = False
t2m = AnalysisTheo(df2a, df2b, shpFilePath, 2, do_plot1, do_plot2)
t3m = AnalysisTheo(df3a, df3b, shpFilePath, 3, do_plot1, do_plot2)
t4m = AnalysisTheo(df4a, df4b, shpFilePath, 4, do_plot1, do_plot2)
t5m = AnalysisTheo(df5a, df5b, shpFilePath, 5, do_plot1, do_plot2)
t2 = t2m.main()
t3 = t3m.main()
t4 = t4m.main()
t5 = t5m.main()

do_plot5 = False
if do_plot5:
    plotHist(t2.df1['dist'], t2.df2['dist'], 2,
             t3.df1['dist'], t3.df2['dist'], 3)
    plotHist(t4.df1['dist'], t4.df2['dist'], t5.df1['dist'], t5.df2['dist'], 5)

# Analyse 2
do_plot6 = False
if do_plot6:
    plotHist2(t5.df1['dist'], t5.df2['dist'], 5)

do_save = False
if do_save:
    # ========= Save as CSV =========
    # Apply the type format according to the dico
    def get_format(df):
        """Apply the right format to each 'df' columns paramter."""
        types = {'timestamp': str,
                 'lon': float,
                 'stdLong': float,
                 'lat': float,
                 'stdLat': float,
                 'alt': float,
                 'stdAlt': float,
                 'sep': float,
                 'rangeRMS': float,
                 'posMode': str,
                 'numSV': float,
                 'difAge': float,
                 'numGP': float,
                 'numGL': float,
                 'numGA': float,
                 'numGB': float,
                 'opMode': float,
                 'navMode': float,
                 'PDOP': float,
                 'HDOP': float,
                 'VDOP': float,
                 'stdMajor': float,
                 'stdMinor': float,
                 'orient': float}
        for col, col_type in types.items():
            df[col] = df[col].astype(col_type, errors='ignore')
        return df

    # Apply Correct Format
    t2.df1 = get_format(t2.df1)
    t2.df2 = get_format(t2.df2)
    t3.df1 = get_format(t3.df1)
    t3.df2 = get_format(t3.df2)
    t4.df1 = get_format(t4.df1)
    t4.df2 = get_format(t4.df2)
    t5.df1 = get_format(t5.df1)
    t5.df2 = get_format(t5.df2)

    # Save as csv
    t2.df1.to_csv(base + 'res/' + 'trajectoire_2_st1' + ".csv")
    t2.df2.to_csv(base + 'res/' + 'trajectoire_2_st2' + ".csv")
    t2.delta.to_csv(base + 'res/' + 'trajectoire_2_distances' + ".csv")
    t3.df1.to_csv(base + 'res/' + 'trajectoire_3_st1' + ".csv")
    t3.df2.to_csv(base + 'res/' + 'trajectoire_3_st2' + ".csv")
    t3.delta.to_csv(base + 'res/' + 'trajectoire_3_distances' + ".csv")
    t4.df1.to_csv(base + 'res/' + 'trajectoire_4_st1' + ".csv")
    t4.df2.to_csv(base + 'res/' + 'trajectoire_4_st2' + ".csv")
    t4.delta.to_csv(base + 'res/' + 'trajectoire_4_distances' + ".csv")
    t5.df1.to_csv(base + 'res/' + 'trajectoire_5_st1' + ".csv")
    t5.df2.to_csv(base + 'res/' + 'trajectoire_5_st2' + ".csv")
    t5.delta.to_csv(base + 'res/' + 'trajectoire_5_distances' + ".csv")
