# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 12:54:01 2021

@author: Michael
"""
import pandas as pd
import iso8601
import pytz
import geopandas as gpd
import math
from lib.plot_theo import plotHistDist,plotHistDist2, plotHist,plotHist2,plotShpLine,plotRefLine

import fiona

class ParseTheo:

    def __init__(self, txt_file):
        self.txt_file = txt_file
        self.shpfile = '.\\maps\\railways\\foward_track.shp'

        # Create Data Frame
        columns = ['timestamp', 'lon', 'stdLong', 'lat', 'stdLat', 'alt',
                   'stdAlt', 'sep', 'rangeRMS', 'posMode', 'numSV',
                   'difAge', 'numGP', 'numGL', 'numGA', 'numGB',
                   'opMode', 'navMode',
                   'PDOP', 'HDOP', 'VDOP', 'stdMajor', 'stdMinor', 'orient',
                   'fixType']

        self.df_out = pd.DataFrame(
            data=None, index=None, columns=columns, dtype=None, copy=False)

    def utcrcf3339(self,date):
        _date_obj = iso8601.parse_date(date)
        _date_utc = _date_obj.astimezone(pytz.utc)
        _date_utc_zformat = _date_utc.strftime('%Y-%m-%dT%H:%M:%S%fZ')
        return _date_utc_zformat


    def distance_pt2shpline(self, point, polyline):
        # Distance minimal entre le point et la linge par itératio
        # C'est pas gönial car je teste toute les distances possible
        d = 90000
        for line in polyline['geometry']:
            d_new = line.distance(point)
            if d_new < d:
                d = d_new
        return d

    def main(self):
        # Open txt file
        df = pd.read_csv(self.txt_file, sep='\t', skiprows=[1],
                         encoding='unicode_escape', dtype=str)

        ## Time converstion
        # Replace 60th second with 0 , because isô8601 accept values between
        # 1 and 59

        # Convert UTC date into utcrcf3339 standard
        df['date'] = df['Year'] + df['Month'].str.zfill(2) +\
                df['Day'].str.zfill(2) + 'T' + \
                df['Hour'].str.zfill(2) +\
                df['Minute'].str.zfill(2) + df['Second']


        df['timestamp'] = df['date'].map(lambda x: self.utcrcf3339(x))

        ## Measure distance from reference
        # Load rails als shapefile
        rail_forth = gpd.read_file(self.shpfile)

        # East/North to gpd points geometry
        gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.East, df.North))

        # Mesure distance from the rail
        dist = [None]*len(df['geometry'])

        for index, row in df.iterrows():
            if not math.isnan(row['geometry'].x) \
                or not math.isnan(row['geometry'].x):
                dist[index] = self.distance_pt2shpline(row['geometry'],
                                                       rail_forth)
        df['dist'] = dist

        # Fill output
        self.df_out['timestamp'] = df['timestamp']
        self.df_out['lon'] = df['East'].astype(float)
        self.df_out['lat'] = df['North'].astype(float)
        self.df_out['alt'] = df['Altitude'].astype(float)
        self.df_out['dist'] = df['dist']

        return self.df_out

class AnalysisTheo:

    def __init__(self, df1, df2, idx, do_plot1, do_plot2):
        self.df1 = df1
        self.df2 = df2
        self.idx = idx
        self.do_plot1 = do_plot1
        self.do_plot2 = do_plot2

    # class Track:
    #     def __init__(self, df1_old,df2_old, mean_old, std_old, delta_old, timedelta_old,
    #                  df,df2, mean, std, delta, timedelta):


    def timeorder(self, df1, df2):

        # Rearrange théodolites series
        # Transform time string to time format
        df1['timestamp'] = pd.to_datetime(df1['timestamp'],
                                 format= '%Y-%m-%dT%H:%M:%S%fZ' )
        df2['timestamp'] = pd.to_datetime(df2['timestamp'],
                                 format= '%Y-%m-%dT%H:%M:%S%fZ' )

        # Sort data by ascending time
        df1 = df1.sort_values(by=['timestamp'])
        df2 = df2.sort_values(by=['timestamp'])
        return df1, df2

    def sync(self, df1, df2):
        # Found minimum overlapping time
        tmin1 = df1['timestamp'].min()
        tmax1 = df1['timestamp'].max()
        tmin2 = df2['timestamp'].min()
        tmax2 = df2['timestamp'].max()

        tmin = max(tmin1, tmin2) # /!\ time min/max are inverted
        tmax = min(tmax1, tmax2) # /!\ time min/max are inverted

        # Get just timelaps that are present in both series
        df1 = df1[(df1['timestamp'] > tmin) & (df1['timestamp'] < tmax)]
        df2 = df2[(df2['timestamp'] > tmin) & (df2['timestamp'] < tmax)]

        # Synchronize the dataframe
        df1,df2 = df1.align(df2)
        return df1, df2

    def stat(self, df1, df2):
         # Statistics
        delta = df1['dist']-df2['dist']
        timedelta = df1['timestamp']-df2['timestamp']
        std = delta.std()
        mean = delta.mean()

        return delta, timedelta, std, mean

    def main(self):

        # Change time format and sortby timstamp
        self.df1,self.df2 = self.timeorder(self.df1,self.df2)
        # Synchronize the dataframe
        self.df1, self.df2 = self.sync(self.df1, self.df2)

        # Statistic
        delta, timedelta, std, mean = self.stat(self.df1, self.df2)

        # Remove values outside 2 times the std
        df1_new = self.df1[(self.df1['dist'] >= mean - std) & \
                           (self.df1['dist'] <= mean + std)]
        df2_new = self.df2[(self.df2['dist'] >= mean - std) & \
                           (self.df2['dist'] <= mean + std)]

        # Synchronize the dataframe
        df1_new, df2_new = self.sync(df1_new, df2_new)

        # Statistic
        delta_new, timedelta_new, std_new, mean_new = self.stat(df1_new, \
                                                                df2_new)

        # plot

        if self.do_plot1:
            # PLOT Figure 1- Obs Brute
            plotHistDist(self.df1,self.df2,delta,shpFilePath, self.idx)
            plotHistDist2(self.df1,self.df2,delta,shpFilePath, self.idx)
        if self.do_plot2:
            # PLOT Figure 1- Obs improved
            plotHistDist(df1_new,df2_new,delta_new,shpFilePath, self.idx)
            plotHistDist2(df1_new,df2_new,delta_new,shpFilePath, self.idx)
        # Prepare Class object output
        self.df1 = df1_new
        self.df2 = df2_new
        self.mean = mean_new
        self.std= std_new
        self.delta = delta_new
        self.timedelta = timedelta_new

        self.df1_old = self.df1
        self.df2_old = self.df2
        self.mean_old = mean
        self.std_old= std
        self.delta_old = delta
        self.timedelta_old = timedelta

        return self

class AnalysisTheo2:

    def __init__(self, df, df2, shpfile_out1,shpfile_out2,shpRailPath,
                 swipos_netr9, swps_blox, sapcorda):
        self.df = df
        self.df2 = df2
        self.shpfile_out1 = shpfile_out1
        self.shpfile_out2 = shpfile_out2
        self.shpRailPath = shpRailPath
        self.spws_ublox = swps_blox
        self.netr9 = swipos_netr9
        self.sapcorda = sapcorda

    def pt2shpline(self, shpfile_out, df):
        # define shapefile schema
        schema = {
                'geometry':'LineString',
                'properties':[('Name','str')]
                }

        #open a fiona object
        lineShp = fiona.open(shpfile_out, mode='w', driver='ESRI Shapefile',
                             schema = schema)

        #get list of points
        xyList = []
        rowTime = ''
        for index, row in df.iterrows():
            xyList.append((row.lon,row.lat))
            rowTime = row.timestamp

        #save record and close shapefile
        rowDict = {
        'geometry' : {'type':'LineString',
                         'coordinates': xyList},
        'properties': {'Name' : rowTime},
        }

        lineShp.write(rowDict)

        #close fiona object
        lineShp.close()
        return lineShp

    def main(self):
        theo1 = self.pt2shpline(self.shpfile_out1, self.df)
        theo2 = self.pt2shpline(self.shpfile_out2, self.df2)
        df_ubx = pd.read_csv(self.spws_ublox)
        df_sap = pd.read_csv(self.sapcorda)
        df_netr9 = pd.read_csv(self.netr9)

        # Plot
        plotRefLine(self.shpfile_out1,self.shpfile_out2,self.shpRailPath,
                    self.df, self.df2)
        # plotShpLine(self.shpfile_out1, self.shpRailPath, self.df, df_netr9,df_ubx,df_sap)
        return theo1, theo2


# Variables decleration utcrcf3339 and distance from the reference
base = './data/Geneva_Théodolites/20210820_livraison/'
shpFilePath = '.\\maps\\railways\\foward_track.shp'

# Get
t2a = ParseTheo(base + 'trajectoire_2_st1.txt')
t2b = ParseTheo(base + 'trajectoire_2_st2.txt')
t3a = ParseTheo(base + 'trajectoire_3_st1.txt')
t3b = ParseTheo(base + 'trajectoire_3_st2.txt')
t4a = ParseTheo(base + 'trajectoire_4_st1.txt')
t4b = ParseTheo(base + 'trajectoire_4_st2.txt')
t5a = ParseTheo(base + 'trajectoire_5_st1.txt')
t5b = ParseTheo(base + 'trajectoire_5_st2.txt')
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
shp2a = base  +  'line/'+ 'trajectoire_2_st1' +".shp"
shp2b = base  +  'line/'+ 'trajectoire_2_st2' +".shp"
shp5a=base  +  'line/'+ 'trajectoire_5_st1' +".shp"
shp5b= base  +  'line/'+ 'trajectoire_5_st2' +".shp"
swipos_ublox = track_file + 'swipos_ublox.csv'
swipos_netr9 = track_file + 'swipos_NetR9-copy__10_30_10_11_10_48.result'
sapcorda = track_file + 'sapcorda.result'
# A = AnalysisTheo2(df2a,df2b,shp5a,shp5b,shpFilePath, swipos_netr9, swipos_ublox, sapcorda)
# B = AnalysisTheo2(df5a,df5b,shp5a,shp5b,shpFilePath, swipos_netr9, swipos_ublox, sapcorda)
# A.main()
# B.main()

## Analyse 1
do_plot0 = False
if do_plot0:
    plotHist(df2a['dist'],df2b['dist'], 2,df3a['dist'],df3b['dist'],3)
    plotHist(df4a['dist'],df4b['dist'], 2,df5a['dist'],df5b['dist'],3)

do_plot1 = True
do_plot2 = False
t2m = AnalysisTheo(df2a, df2b, 2, do_plot1, do_plot2)
t3m = AnalysisTheo(df3a, df3b, 3, do_plot1, do_plot2)
t4m = AnalysisTheo(df4a, df4b, 4, do_plot1, do_plot2)
t5m = AnalysisTheo(df5a, df5b, 5, do_plot1, do_plot2)
t2 = t2m.main()
t3 = t3m.main()
t4 = t4m.main()
t5 = t5m.main()

do_plot5 = False
if do_plot5:
    plotHist(t2.df1['dist'],t2.df2['dist'], 2,t3.df1['dist'],t3.df2['dist'],3)
    plotHist(t4.df1['dist'],t4.df2['dist'],t5.df1['dist'],t5.df2['dist'],5)

# Analyse 2
do_plot6 = False
if do_plot6:
    plotHist2(t5.df1['dist'],t5.df2['dist'],5)

do_save = False
if do_save:

    # ========= Save as CSV =========
    # Apply the type format according to the dico
    def get_format(df):
        types = {'timestamp':str,
                        'lon':float,
                        'stdLong':float,
                        'lat':float,
                        'stdLat':float,
                        'alt':float,
                        'stdAlt':float,
                        'sep':float,
                        'rangeRMS':float,
                        'posMode':str,
                        'numSV':float,
                        'difAge': float,
                        'numGP':float,
                        'numGL':float,
                        'numGA':float,
                        'numGB':float,
                        'opMode':float,
                        'navMode':float,
                        'PDOP':float,
                        'HDOP':float,
                        'VDOP':float,
                        'stdMajor':float,
                        'stdMinor':float,
                        'orient':float}
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
    t2.df1.to_csv(base  +  'res/'+ 'trajectoire_2_st1' +".csv")
    t2.df2.to_csv(base  +  'res/'+ 'trajectoire_2_st2' +".csv")
    t2.delta.to_csv(base  +  'res/'+ 'trajectoire_2_distances' +".csv")
    t3.df1.to_csv(base  +  'res/'+ 'trajectoire_3_st1' +".csv")
    t3.df2.to_csv(base  +  'res/'+ 'trajectoire_3_st2' +".csv")
    t3.delta.to_csv(base  +  'res/'+ 'trajectoire_3_distances' +".csv")
    t4.df1.to_csv(base  +  'res/'+ 'trajectoire_4_st1' +".csv")
    t4.df2.to_csv(base  +  'res/'+ 'trajectoire_4_st2' +".csv")
    t4.delta.to_csv(base  +  'res/'+ 'trajectoire_4_distances' +".csv")
    t5.df1.to_csv(base  +  'res/'+ 'trajectoire_5_st1' +".csv")
    t5.df2.to_csv(base  +  'res/'+ 'trajectoire_5_st2' +".csv")
    t5.delta.to_csv(base  +  'res/'+ 'trajectoire_5_distances' +".csv")


