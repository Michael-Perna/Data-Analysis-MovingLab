# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 11:17:43 2021

@author: Michael

"""



# Module importation
from lib.import_df import StatDf
from lib.plot_stat import StatPLot as tools
import matplotlib.pyplot as plt
import os
import lib.gui_statistic as gui
import pandas as pd
import geopandas as gpd
from geopandas.tools import sjoin
import numpy as np
import shapefile
from tqdm import tqdm
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
'''
apri results file
media distanca
std deviation distanca

percentuale di fissi
percentuale di fissi > 10 cm

time to fix = media et standart deviations
'''

def _pdf_cdf(df):
    # Drop epochs with no positions or inf position
    df['dist'].replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df['dist'].dropna()
    dist = df.to_numpy()

    # Get Quantile
    quantile = np.nanquantile(dist,
                             [0.5,0.75,0.9],
                             keepdims=False)
    # Define bins sequence
    bins = np.append(np.arange(0, 20, 0.01),np.arange(20, max(dist), 1))

    # Get counts from numpy.histogram
    counts, bins = np.histogram(dist, bins=bins)

    # Probability Density Function :
    N = sum(counts)
    PDF= counts/N
    weights = np.ones_like(dist)/N  # Used to normalized the histogram

    # Cumulative Densitive Function
    CDF = np.cumsum(PDF)

    return dist, bins, weights, CDF, quantile


class Statistic:
    def __init__(self, sourcefile, savepath, receiver):

        self.sourcefile = sourcefile
        self.save_path = savepath
        self.receiver = receiver
        self.loop_shp = './maps/railways/loops.shp'
        self.rail_f = shapefile.Reader('.\\maps\\railways\\foward_track.shp')
        self.rail_b = shapefile.Reader('.\\maps\\railways\\backward_track.shp')
        self.header=['timestamp','lon', 'lat', 'posMode','numSV',
                     'difAge','HDOP','dist']
        self.columns_head = ['start', 'end', 'num_elem',
                            'median', 'mean', 'std',
                            'RTK_Fix', 'median1', 'mean1', 'std1',
                            'RTK_Float', 'median2', 'mean2', 'std2',
                            'DGNSS_Fix', 'median3', 'mean3', 'std3',
                            'DGNSS_Auto', 'median4', 'mean4', 'std4',
                            'No_Fix', 'No_Pos', 'Continuity'
                            ]

        # Clean Data
        self.plt_bad_days = False

        # INTEGRITY
        self.do_integrity = True


        # CONTINUITY
        self.do_continuity = False

        # ACCURACY
        self.do_accuracy = True

        # PDF CDF Histogram Plot
        self.do_plt1 = False
        save_plt1 = True
        self.do_xlim = True
        f_hist = self.save_path + 'fig/' + 'Accuracy_PDF_CFD.png'
        self.f_hist = [save_plt1, f_hist]

        # DISPONIBILITY
        self.do_disponibility = True

        # SPATIAL ANALYSIS
        self.do_spatial = False

    def continuity(self, df, time):
        failEvent = 1
        eventDuration = 0
        n=0
        dT = pd.DataFrame(columns=['dT_Fail'])
        df = df.reset_index(drop=True)
        # Progress bar
        loop = tqdm(total = len(df.index) , position =0, desc='Calculating MTBF')
        i = 0
        continuity = np.empty([len(df.index),3])
        continuity[:] = np.nan

        start = False
        for index in df.index[:-1]:
            Ts = df.iloc[index,0]
            delta = df['timestamp'].iloc[index+1] - df['timestamp'].iloc[index]
            if delta.seconds > 300 and start : # This is considered as a new track event after 5 minutes of connection loss
                T =  df.iloc[index+1,0] - Ts
                continuity[i][0] = dT.mean()[0].seconds/T.seconds
                continuity[i][1] = T.seconds
                continuity[i][2] = dT.mean()[0].seconds
                i+=1
                Ts=df.iloc[index+1,0]
                start = False
            if df['posMode'].iloc[index]!='RTK fixed' or delta.seconds > 5 :
                eventDuration += 1
                # Si la pèrte du fixe dure plus que dix seconde on considère
                # comme un événement de 'fail'
                if eventDuration >= 10 :
                    eventDuration = 0         # Reset count

                if failEvent == 1:
                    Tstart = df.iloc[index,0] # Keep trace f the time of the event
                    failEvent += 1
                if failEvent ==2:
                    start = True
                    Tend = df.iloc[index,0]
                    dT.loc[n] = [Tend - Tstart]
                    failEvent == 0          # Reset count of Fail Event
                    Tstart = df.iloc[index,0]# Reset Start Time
                    n +=1

            loop.update(1)
        T =  df.iloc[index+1,0] - Ts
        if T.seconds > 1:
            continuity[i][0] = dT.mean()[0].seconds/T.seconds
            continuity[i][1] = T.seconds
            continuity[i][2] = dT.mean()[0].seconds
        loop.close()

        return continuity
    def posMode(self, time,df, df_nf,df_ag,df_dg,df_rf,df_rfl):
        # Calculate Statistic by Fix Type
        if 'dist' in df.columns:
            posMode = {
                'start':df['timestamp'].iloc[0],
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
                'No_Pos': (time['epochsNotnan']-len(df_rf)-len(df_rfl)-len(df_dg)-len(df_ag)-len(df_nf))/ time['epochsNotnan']
                }
        return posMode

    def posDist(self, time,df, df10, df25, df50, df100, df500, dfinf):
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

    def posInteg(self, df_rf):

        df_rf_wrong = df_rf[(df_rf['dist']>0.5)]
        df_rf_wrong1= df_rf[(df_rf['dist']>1)]
        df_rf_wrong2 = df_rf[(df_rf['dist']>2)]

        # Replace NaN HDOP with 1000
        df_rf_wrong.HDOP.fillna(10000,inplace=True)
        df_rf_wrong1.HDOP.fillna(10000,inplace=True)
        df_rf_wrong2.HDOP.fillna(10000,inplace=True)

        p50= len(df_rf_wrong)/len(df_rf)
        p100= len(df_rf_wrong1)/len(df_rf)
        p200= len(df_rf_wrong2)/len(df_rf)

        corrHDOP_50 = np.corrcoef(df_rf_wrong.HDOP,df_rf_wrong.dist)       # No
        corrNumSV_50 = np.corrcoef(df_rf_wrong.numSV,df_rf_wrong.dist)     # Sligltly negative for Net -12%
        corrDifAge_50 = np.corrcoef(df_rf_wrong.difAge,df_rf_wrong.dist)   # No

        corrHDOP_200 = np.corrcoef(df_rf_wrong2.HDOP,df_rf_wrong2.dist)       # No
        corrNumSV_200 = np.corrcoef(df_rf_wrong2.numSV,df_rf_wrong2.dist)     # Sligltly negative for Net -12%
        corrDifAge_200 = np.corrcoef(df_rf_wrong2.difAge,df_rf_wrong2.dist)   # No

        corrHDOP_100 = np.corrcoef(df_rf_wrong1.HDOP,df_rf_wrong1.dist)       # No
        corrNumSV_100 = np.corrcoef(df_rf_wrong1.numSV,df_rf_wrong1.dist)     # Sligltly negative for Net -12%
        corrDifAge_100 = np.corrcoef(df_rf_wrong1.difAge,df_rf_wrong1.dist)   # No


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
            'corrDifAge_50':corrDifAge_50,
            'p50':p50,
            'p100':p100,
            'p200':p200,
            'corrHDOP_100': corrHDOP_100,
            'corrNumSV_100': corrNumSV_100,
            'corrDifAge_100':corrDifAge_100,
            'corrHDOP_200': corrHDOP_200,
            'corrNumSV_200': corrNumSV_200,
            'corrDifAge_200':corrDifAge_200
            }
        return integrity

    def main(self):

        # EXTRACT DATA
        head, tail = os.path.split(self.sourcefile)
        print('Data frame initialization : ', tail)
        timeseries = StatDf(self.sourcefile, self.header)
        df, valid = timeseries.get_df()

        if not valid:
            return

        # CLEAN DATA FROM DATA OUT OF REFERENCE
        # Remove Position taken by night as the tram is in the depôt
        df = df.set_index(pd.to_datetime(df['timestamp']))
        # df = df.between_time('7:00','0:00')

        # Ignore days where the tram took paths outside the reference
        if self.plt_bad_days:
            fig, ax = plt.subplots()
            # ax.scatter(df.lon, df.lat)
            # ax.scatter(df.loc['2021-04-26'].lon, df.loc['2021-04-26'].lat,label ='2021-04-26')
            # ax.scatter(df.loc['2021-0-06'].lon, df.loc['2021-07-06'].lat,label ='2021-06-06')
            ax.scatter(df.loc['2021-03-22'].lon, df.loc['2021-03-22'].lat,label ='2021-03-22')
            # ax.scatter(df.loc['2021-07-21'].lon, df.loc['2021-07-21'].lat,label ='2021-07-21')
            ax.legend()

        df = df.drop( df.loc['2021-03-18'].index)
        df = df.drop( df.loc['2021-03-19'].index)
        df = df.drop( df.loc['2021-03-22'].index)
        df = df.drop( df.loc['2021-03-28'].index)
        df = df.drop( df.loc['2021-03-31'].index)
        df = df.drop( df.loc['2021-04-17'].index)
        df = df.drop( df.loc['2021-06-07'].index)
        df = df.drop( df.loc['2021-04-26'].index)
        df = df.drop( df.loc['2021-06-07'].index)
        df = df.drop( df.loc['2021-07-21'].index)
        df = df.drop( df.loc['2021-07-28'].index)

        print('Get time statistic')
        # Time statistics
        time = {'start':df['timestamp'].iloc[0],
                'end': df['timestamp'].iloc[-1],
                'T': df['timestamp'].iloc[-1]-df['timestamp'].iloc[0],
                'epochs': len(df),
                'epochsNotnan': len(df[~np.isnan(df.lon)])
                }

        # CLASSIFY ACCORDINGLY POTITION MODE
        df_nf = df[df['posMode']=='No fix']                 # No fix
        df_ag = df[df['posMode']=='Autonomous GNSS fix']    # Autonomous GNSS fix
        df_dg = df[df['posMode']=='Differential GNSS fix']  # Differential GNSS fix
        df_rf = df[df['posMode']=='RTK fixed']              # RTK fixed
        df_rfl = df[df['posMode']=='RTK float']             # RTK float
        df_nrf =  df[df['posMode']!='RTK fixed']            # all position which are not RTK fixed

        # CLASSIFY ACCORDINGLY pRECISION
        df10 = df[(df['dist']<=0.10)]
        df25 = df[(df['dist']>0.10) & (df['dist']<=0.25)]
        df50 = df[(df['dist']>0.25) & (df['dist']<=0.50)]
        df100 = df[(df['dist']>0.50) & (df['dist']<=1)]
        df500 = df[(df['dist']>1) & (df['dist']<=5)]
        dfinf = df[(df['dist']>5)]

        # INTEGRITY
        if self.do_integrity:
            print('Estimating Integrity')
            integrity = self.posInteg(df_rf)
            # kSigma Integrity diagram
            # hpl = df_rf.HDOP *0.03
            # hpe = df_rf.dist

            # # Plot Standfort Integrity Diagram
            # fig, ax = plt.subplots()
            # ax.scatter(hpe, hpl)

            # # Plot Standfort Integrity Diagram
            # fig, ax = plt.subplots()
            # ax.scatter(hpe, hpl)

        else:
            integrity = []

        # ACCURACY
        if self.do_accuracy:
            print('Estimating Accuracy')

            # Probability Density Function PDF
            dist, bins, weights, CDF, quantile = _pdf_cdf(df)
                    # Plot Accuracy Histogram
            if self.do_plt1:
                print('Plot Accuracy Distance' )
                tools.plotHistAcc(dist,bins,weights,CDF,quantile,self.f_hist,
                                  self.receiver, self.do_xlim)

        else:
            quantile = []


        # CONTINUITY
        if self.do_continuity:
            print('Estimating Continuity')
            continuity = self.continuity(df, time)
            cont= continuity[:,0][~np.isnan(continuity[:,0])]
            # weights= continuity[:,1][~np.isnan(continuity[:,1])]
            continuity = np.average(cont)
        else:
            continuity = []


        # DISPONIBILITY
        if self.do_disponibility:
            print('Estimating disponibility')
            posMode = self.posMode(time,df_rf, df_nf,df_ag,df_dg,df_rf,df_rfl)
            posDist = self.posDist(time,df, df10, df25, df50, df100, df500, dfinf)
        else:
            posMode = []
            posDist=[]


        # SPATIAL ANALYSIS
        if self.do_spatial:
            print('Spatial Analysis')
            df100 = df[(df['dist']>2)]
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
            ax.plot(range(len(df.dist)),df.dist)


        return df, continuity, posMode, posDist, integrity, quantile

# In[]:
# Call the interface class
# app = gui.Interface()
# app.title('Parse UBX messages')
# app.mainloop()
# filepath, receiver = app.output()

filepath = './res/data/ublox.data'
filepath2 = './res/data/sapcorda.data'
filepath3 = './res/data/NetR9.data'

filepath = './res/data/ublox_zone2.data'
filepath2 = './res/data/sapcorda_zone2.data'
filepath3 = './res/data/NetR9_zone2.data'

filepath = './res/data/ublox_zone4.data'
filepath2 = './res/data/sapcorda_zone4.data'
filepath3 = './res/data/NetR9_zone4.data'

# csvpath = './res/data/ublox_zone2.csv'
# csvpath2 = './res/data/sapcorda_zone2.csv'
# csvpath3 = './res/data/NetR9_zone2.csv'

save_path1 = './res/stat/swipos/'
save_path2 = './res/stat/sapcorda/'
save_path3 = './res/stat/NetR9/'

header=['timestamp','lon', 'lat', 'posMode','numSV','difAge','HDOP','dist']

# Executre once for the selcted file
if os.path.isfile(filepath):
    tracks = Statistic(filepath, save_path1,'u-blox avec swipos')
    df, continuity, posMode,posDist, integrity, quantile = tracks.main()
    # df.to_csv(csvpath, sep=',', na_rep='', columns=header, header=True,index=False,line_terminator = '\n')

# Executre once for the selcted file
if os.path.isfile(filepath2):
    tracks = Statistic(filepath2, save_path2, 'u-blox avec SAPA')
    df2, continuity2, posMode2,posDist2, integrity2, quantile2 = tracks.main()
    # df2.to_csv(csvpath2, sep=',', na_rep='', columns=header, header=True,index=False,line_terminator = '\n')

# Executre once for the selcted file
if os.path.isfile(filepath3):
    tracks = Statistic(filepath3, save_path3, 'NetR9 avec swipos')
    df3, continuity3, posMode3, posDist3, integrity3, quantile3 = tracks.main()
    # df3.to_csv(csvpath3, sep=',', na_rep='', columns=header, header=True,index=False,line_terminator = '\n')


# PLot Histogram HPE
do_xlim = True
save_plt1 = False

if False:
    fname2 = './res/stat/Accuracy_PDF_CFD_swipos_sapos.png'
    fname3 = './res/stat/Accuracy_PDF_CFD_netr9_ublox.png'

    receiver = 'u-blox avec RTK VRS GIS/GEO swipos'
    receiver2 = 'u-blox avec PPP-RTK SAPOS'
    receiver3 = 'NetR9 avec RTK VRS GIS/GEO swipos'

    fname2 = [save_plt1, fname2]
    fname3 = [save_plt1, fname3]

    dist, bins, weights, CDF, quantile = _pdf_cdf(df)
    dist2, bins2, weights2, CDF2, quantile2 = _pdf_cdf(df2)
    dist3, bins3, weights3, CDF3, quantile3 = _pdf_cdf(df3)


    tools.plotHistAcc2(dist,bins,weights,CDF,quantile, receiver,'blue',
                        dist2,bins2,weights2,CDF2,quantile2,fname2, receiver2,'orange', do_xlim)

    tools.plotHistAcc2(dist,bins,weights,CDF,quantile, receiver,'blue',
                        dist3,bins3,weights3,CDF3,quantile3,fname3, receiver3,'red', do_xlim )

    # Plot HPE
    tools.plot_HPE(df, df2, df3, receiver,receiver2,receiver3, posMode,posMode2,posMode2)



# ANALYSY
# integrity['dist'][[integrity['dist']>2]]
