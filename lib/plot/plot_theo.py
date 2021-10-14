# -*- coding: utf-8 -*-
"""
Created on Sun Aug 22 08:15:31 2021

@author: Michael
"""
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import shapefile


def plotHistDist(df_st1,df_st2,delta,shpFilePath, idx):

    # Load rails als shapefile

    rail_forth = shapefile.Reader(shpFilePath)

    # Define figure
    fig, axs = plt.subplots(2,2)

    # Define Main set_title
    fig.suptitle(' Trajectoire numéro #%i' %idx,
                     backgroundcolor='blue',
                     color='white')

    # SUBPLOT 221 : obsérvations planimétrie
    # Chemin de fer
    i =0
    for shape in rail_forth.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        if i == 3:
            axs[0,0].plot(x, y, label='Référence', color='black')
        i+=1

    # Observations des théodolités
    axs[0,0].scatter(df_st1['lon'],df_st1['lat'],label='théodolite 1',color='red')
    axs[0,0].scatter(df_st2['lon'],df_st2['lat'], label='théodolite 2',color='blue')
    axs[0,0].set_title('Planimétrie en MN95 trajectoire #%i'%(idx))

    # Box / axis Limit
    _xmin = df_st2['lon'].min()-100
    _xmax = df_st2['lon'].max()+100
    _ymin = df_st2['lat'].min()-100
    _ymax = df_st2['lat'].max()+100

    y_formatter = ScalarFormatter(useOffset=False, useMathText=True)
    axs[0,0].yaxis.set_major_formatter(y_formatter)
    x_formatter = ScalarFormatter(useOffset=False,useMathText=True)
    axs[0,0].yaxis.set_major_formatter(x_formatter)

    axs[0,0].set_xlim([_xmin,_xmax])
    axs[0,0].set_ylim([_ymin,_ymax])
    axs[0,0].legend()
    # SUBPLOT 222 : distance differences
    axs[0,1].scatter(df_st2['timestamp'],delta)

    # Labels
    axs[0,1].set_ylabel('$\Delta$ ecarts des théodolites [m]')
    axs[0,1].set_xlabel('Temps')
    axs[0,1].set_title('Differances des écarts avec la référence entre les deux théodolité')

    # SUBPLOT 223 : Histogram of difference in distances
    n, bins, patches = axs[1,0].hist(delta, 'auto', facecolor='blue')

    # # Color Histogram
    # # We'll color code by height, but you could use any scalar
    # fracs = n / n.max()
    # # we need to normalize the data to 0..1 for the full range of the colormap
    # norm =  matplotlib.colors.Normalize(fracs.min(), fracs.max())

    # # Now, we'll loop through our objects and set the color of each accordingly
    # for thisfrac, thispatch in zip(fracs, patches):
    #     color =  plt.cm.viridis(norm(thisfrac))
    #     thispatch.set_facecolor(color)

    # Labels
    axs[1,0].set_xlabel('Differances des écarts avec la référence entre les deux théodolites [m]')
    axs[1,0].set_ylabel('Nombre d\observations')
    axs[1,0].set_title('Histogram of difference to the reference')
    axs[1,0].grid(True)
    # fig.colorbar(fracs)


    # SUBPLOT 223 : Histogram of difference in distances
    # Chemin de fer
    i =0
    for shape in rail_forth.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        if i == 3:
            axs[1,1].plot(x, y, label='Référence', color='black')
        i+=1

    # Observations des théodolités
    axs[1,1].scatter(df_st1['lon'],df_st1['lat'],label='théodolite 1',color='red')
    axs[1,1].scatter(df_st2['lon'],df_st2['lat'], label='théodolite 2',color='blue')
    axs[1,1].set_title('Planimétrie en MN95 trajectoire #%i'%(idx))

    # Box / axis Limit
    _xmin = df_st2['lon'].min()-100
    _xmax = df_st2['lon'].max()+100
    _ymin = df_st2['lat'].min()-100
    _ymax = df_st2['lat'].max()+100

    y_formatter = ScalarFormatter(useOffset=False, useMathText=True)
    axs[1,1].yaxis.set_major_formatter(y_formatter)
    x_formatter = ScalarFormatter(useOffset=False,useMathText=True)
    axs[1,1].yaxis.set_major_formatter(x_formatter)

    axs[1,1].set_xlim([_xmin,_xmax])
    axs[1,1].set_ylim([_ymin,_ymax])
    axs[1,1].legend()
    plt.show()

def plotHistDist2(df_st1,df_st2,delta,shpFilePath, idx):

    # Load rails als shapefile
    rail_forth = shapefile.Reader(shpFilePath)

    # Define figure
    px = 1/plt.rcParams['figure.dpi']
    fig, axs = plt.subplots(1,2, figsize=(2000*px, 800*px))

    # Define Main set_title
    fig.suptitle(' Trajectoire numéro #%i' %idx,
                     backgroundcolor='blue',
                     color='white',fontsize=18)


    # SUBPLOT 122 : distance differences
    import pandas as pd
    df_st2['timestamp'] = pd.to_datetime(df_st2['timestamp'],
                                         format='%H:%M:s')
    axs[0].scatter(df_st2['timestamp'],delta)
    # plt.xticks(rotation = 45)

    # Labels
    axs[0].set_ylabel('$\Delta$ écarts entre les théodolites [m]',fontsize=16)
    axs[0].set_xlabel('Temps',fontsize=16)
    axs[0].set_xticklabels(df_st2['timestamp'].dt.strftime('%H:%M'), rotation = 45)
    # axs[0].set_title('Differances des écarts avec la référence entre les deux théodolité',fontsize=18)

    # SUBPLOT 223 : Histogram of difference in distances
    n, bins, patches = axs[1].hist(delta, 'auto', facecolor='blue')


    # Labels
    axs[1].set_xlabel('$\Delta$ écarts entre les théodolites [m]',fontsize=16)
    axs[1].set_ylabel('Nombre d\observations',fontsize=16)
    # axs[1].set_title('Difference to the reference',fontsize=18)
    xlabels = df_st2['timestamp']

    axs[1].grid(True)

    plt.rc('font', size=18)


    # Box / axis Limit
    _xmin = df_st2['lon'].min()-100
    _xmax = df_st2['lon'].max()+100
    _ymin = df_st2['lat'].min()-100
    _ymax = df_st2['lat'].max()+100

    plt.show()

def plotHist(d1a,d1b, idx1,d2a,d2b,idx2):

    # Define figure
    fig, axs = plt.subplots(2,2)
    # Define Main set_title
    fig.suptitle(' Histogrammes des distances avec la référence',
                     backgroundcolor='blue',
                     color='white')

    # SUBPLOT 221 : Histogramm 1
    n, bins, patches = axs[0,0].hist(d1a, 'auto', density=True, facecolor='blue')

    # Labels
    m = d1a.mean()
    m2 = d1a.median()
    s = d1a.std()

    axs[0,0].set_xlabel('Distance entre les points du théodolite et la référence')
    axs[0,0].set_ylabel('Nombre d\'observations')
    axs[0,0].set_title('Théodolité #2, Trajectoire #%i, mean: %.3f, median: %.3f std: %.3f'%(idx1, m,m2, s))
    axs[0,0].grid(True)

    # SUBPLOT 222 : Histogramm 2
    n, bins, patches = axs[0,1].hist(d1b, 'auto', density=True, facecolor='blue')

    # Labels
    axs[0,1].set_xlabel('Distance entre les points du théodolite et la référence')
    axs[0,1].set_ylabel('Nombre d\'observations')
    axs[0,1].set_title('Théodolité #2, Trajectoire #%i, mean: %.3f, median: %.3f, std: %.3f'
                       %(idx1,d1b.mean(),d1b.median(),d1b.std()))
    axs[0,1].grid(True)

    # SUBPLOT 223 : Histogram 3
    n, bins, patches = axs[1,0].hist(d2a, 'auto', density=True, facecolor='blue')
    # Labels
    axs[1,0].set_xlabel('Distance entre les points du théodolite et la référence',fontsize=16)
    axs[1,0].set_ylabel('Nombre d\'observations',fontsize=16)
    axs[1,0].set_title('Théodolite #1, Trajectoire #%i, mean: %.3f, median: %.3f, std: %.3f'
                       %(idx2,d2a.mean(),d2a.median(),d2a.std()),fontsize=18)
    axs[1,0].grid(True)

    # SUBPLOT 224 : Histogram 4
    n, bins, patches = axs[1,1].hist(d2b, 'auto', density=True, facecolor='blue')
    # Labels
    axs[1,1].set_xlabel('Distance entre les points du théodolite et la référence [cm]',fontsize=16)
    axs[1,1].set_ylabel('Nombre d\'observations' ,fontsize=16)
    axs[1,1].set_title('Théodolité #2, Trajectoire #%i, mean: %.3f, median: %.3f, std: %.3f'
                       %(idx2,d2b.mean(),d2b.median(),d2b.std()),fontsize=18)
    axs[1,1].grid(True)
    plt.show()

def plotHist2(d1a,d1b, idx1):

    # Define figure
    px = 1/plt.rcParams['figure.dpi']
    fig, axs = plt.subplots(1,2,figsize=(2000*px, 800*px))

    # # Define Main set_title
    # fig.suptitle(' Histogrammes des distances avec la référence',
    #                  backgroundcolor='blue',fontsize=24,
    #                  color='white')

    # SUBPLOT 221 : Histogramm 1
    n, bins, patches = axs[0].hist(d1a, 'auto', density=True, facecolor='blue')

    # Labels
    m = d1a.mean()
    m2 = d1a.median()
    s = d1a.std()

    axs[0].set_xlabel('Distance entre les points du théodolite et la référence [m]',fontsize=16)
    axs[0].set_ylabel('Nombre d\'observations',fontsize=16)
    axs[0].set_title('Théodolité #1, Trajectoire #%i,\n$\mu$: %.3f, median: %.3f $\sigma$: %.3f'%(idx1, m,m2, s)
                     ,fontsize=16)
    plt.xticks(fontsize = 16)
    axs[0].grid(True)

    # SUBPLOT 222 : Histogramm 2
    n, bins, patches = axs[1].hist(d1b, 'auto', density=True, facecolor='blue')

    # Labels
    axs[1].set_xlabel('Distance entre la mesure théodolite et la référence [m]',fontsize=16)
    axs[1].set_ylabel('Nombre d\'observations',fontsize=16)
    axs[1].set_title('Théodolité #2, Trajectoire #%i, \n$\mu$: %.3f, median: %.3f, $\sigma$: %.3f'
                       %(idx1,d1b.mean(),d1b.median(),d1b.std()),
                     fontsize=16)
    axs[1].grid(True)
    plt.rc('font', size=18)

    plt.show()


def plotShpLine(shp1,shp2,df,df1,df2,df3):

    # Load rails als shapefile
    shp1 = shapefile.Reader(shp1)
    shp2 = shapefile.Reader(shp2)

    # Chemin de fer
    # Observations des swipos
    plt.scatter(df['lon'],df['lat'], label='théodolite')
    plt.scatter(df1['lon'],df1['lat'], label='netr9')
    plt.scatter(df2['lon'],df2['lat'], label='ublox swipos')
    plt.scatter(df3['lon'],df3['lat'], label='ublox sapcorda')

    for shape in shp1.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y)
    for shape in shp2.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y)

    # Box / axis Limit
    _xmin = df['lon'].min()-100
    _xmax = df['lon'].max()+100
    _ymin = df['lat'].min()-100
    _ymax = df['lat'].max()+100

    plt.xlim([_xmin,_xmax])
    plt.ylim([_ymin,_ymax])
    plt.legend()
    plt.show()

def plotShpLine(shp1,shp2,df,df1,df2,df3):

    # Load rails als shapefile
    shp1 = shapefile.Reader(shp1)
    shp2 = shapefile.Reader(shp2)

    # SUBPLOT 221 : obsérvations planimétrie
    # Chemin de fer
    # Observations des swipos
    plt.scatter(df['lon'],df['lat'], label='théodolite')
    plt.scatter(df1['lon'],df1['lat'], label='netr9')
    plt.scatter(df2['lon'],df2['lat'], label='ublox swipos')
    plt.scatter(df3['lon'],df3['lat'], label='ublox sapcorda')

    for shape in shp1.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y)
    for shape in shp2.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y)

    # Box / axis Limit
    _xmin = df['lon'].min()-100
    _xmax = df['lon'].max()+100
    _ymin = df['lat'].min()-100
    _ymax = df['lat'].max()+100

    plt.xlim([_xmin,_xmax])
    plt.ylim([_ymin,_ymax])
    plt.legend()
    plt.show()


def plotRefLine(shp1,shp2,rail,df, df2):
    # Load rails als shapefile
    shp1 = shapefile.Reader(shp1)
    shp2 = shapefile.Reader(shp2)
    rail = shapefile.Reader(rail)

    plt.scatter(df['lon'],df['lat'])
    plt.scatter(df2['lon'],df2['lat'])

    for shape in shp1.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y, label='Théodolite 1')
    for shape in shp2.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y,label='Théodolite 2')

    for shape in rail.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y)

    # Box / axis Limit
    _xmin = df['lon'].min()-100
    _xmax = df['lon'].max()+100
    _ymin = df['lat'].min()-100
    _ymax = df['lat'].max()+100

    plt.xlim([_xmin,_xmax])
    plt.ylim([_ymin,_ymax])
    plt.legend()
    plt.show()
