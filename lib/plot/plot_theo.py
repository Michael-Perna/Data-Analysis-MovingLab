# -*- coding: utf-8 -*-
"""
Created on Sun Aug 22 08:15:31 2021.

@author: Michael
"""
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import shapefile
import pandas as pd


def plotHistDist(df_st1: object, df_st2: object, delta: list, shpFilePath: str,
                 idx: int):
    """
    Plot histogram of distances od delta dist and the planimetric obs.

    Parameters
    ----------
    df_st1 : dataframe
        Dataframe with the data of the first theo.
    df_st2 : dataframe
        Dataframe with the data of the second theodolotites.
    delta : list
        Difference of distances with the reference between the two theodolites.
    shpFilePath : str
        Rail forth shapefile path.
    idx : int
        Number of the observation (between 2 and 5).

    Returns
    -------
    None

    """
    # Load rails als shapefile
    rail_forth = shapefile.Reader(shpFilePath)

    # Define figure
    fig, axs = plt.subplots(2, 2)

    # Define Main set_title
    fig.suptitle(' Trajectoire numéro #%i' % idx,
                 backgroundcolor='blue',
                 color='white')

    # -------------------------------------------------------------------------
    # SUBPLOT 221 : obsérvations planimétrie
    # -------------------------------------------------------------------------
    i = 0
    for shape in rail_forth.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        if i == 3:
            axs[0, 0].plot(x, y, label='Référence', color='black')
        i += 1

    # Observations des théodolités
    axs[0, 0].scatter(df_st1['lon'], df_st1['lat'],
                      label='théodolite 1', color='red')
    axs[0, 0].scatter(df_st2['lon'], df_st2['lat'],
                      label='théodolite 2', color='blue')
    axs[0, 0].set_title('Planimétrie en MN95 trajectoire #%i' % (idx))

    # Box / axis Limit
    _xmin = df_st2['lon'].min()-100
    _xmax = df_st2['lon'].max()+100
    _ymin = df_st2['lat'].min()-100
    _ymax = df_st2['lat'].max()+100

    y_formatter = ScalarFormatter(useOffset=False, useMathText=True)
    axs[0, 0].yaxis.set_major_formatter(y_formatter)
    x_formatter = ScalarFormatter(useOffset=False, useMathText=True)
    axs[0, 0].yaxis.set_major_formatter(x_formatter)

    axs[0, 0].set_xlim([_xmin, _xmax])
    axs[0, 0].set_ylim([_ymin, _ymax])
    axs[0, 0].legend()

    # -------------------------------------------------------------------------
    # SUBPLOT 222 : distance differences
    # -------------------------------------------------------------------------
    axs[0, 1].scatter(df_st2['timestamp'], delta)

    # Labels
    axs[0, 1].set_ylabel('$\Delta$ ecarts des théodolites [m]')
    axs[0, 1].set_xlabel('Temps')
    axs[0, 1].set_title(
        'Differances des écarts avec la référence entre les deux théodolité')

    # -------------------------------------------------------------------------
    # SUBPLOT 223 : Histogram of difference in distances
    # -------------------------------------------------------------------------
    n, bins, patches = axs[1, 0].hist(delta, 'auto', facecolor='blue')

    # Labels
    xtext = ' '.join('Differances des écarts avec la référence entre',
                     ' les deux théodolites [m]')
    axs[1, 0].set_xlabel(xtext)
    axs[1, 0].set_ylabel('Nombre d\'observations')
    axs[1, 0].set_title('Histogram of difference to the reference')
    axs[1, 0].grid(True)
    # fig.colorbar(fracs)

    # -------------------------------------------------------------------------
    # SUBPLOT 223 : Histogram of difference in distances
    # -------------------------------------------------------------------------
    i = 0
    for shape in rail_forth.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        if i == 3:
            axs[1, 1].plot(x, y, label='Référence', color='black')
        i += 1

    # Observations des théodolités
    axs[1, 1].scatter(df_st1['lon'], df_st1['lat'],
                      label='théodolite 1', color='red')
    axs[1, 1].scatter(df_st2['lon'], df_st2['lat'],
                      label='théodolite 2', color='blue')
    axs[1, 1].set_title('Planimétrie en MN95 trajectoire #%i' % (idx))

    # Box / axis Limit
    _xmin = df_st2['lon'].min()-100
    _xmax = df_st2['lon'].max()+100
    _ymin = df_st2['lat'].min()-100
    _ymax = df_st2['lat'].max()+100

    y_formatter = ScalarFormatter(useOffset=False, useMathText=True)
    axs[1, 1].yaxis.set_major_formatter(y_formatter)
    x_formatter = ScalarFormatter(useOffset=False, useMathText=True)
    axs[1, 1].yaxis.set_major_formatter(x_formatter)

    axs[1, 1].set_xlim([_xmin, _xmax])
    axs[1, 1].set_ylim([_ymin, _ymax])
    axs[1, 1].legend()
    plt.show()


def plotHistDist2(df_st1: object, df_st2: object, delta: list,
                  shpFilePath: str, idx: int):
    """
    Plot histogram of distances and delta dist and the delta time series.

    Parameters
    ----------
    df_st1 : dataframe
        Dataframe with the data of the first theo.
    df_st2 : dataframe
        Dataframe with the data of the second theodolotites.
    delta : list
        Difference of distances with the reference between the two theodolites.
    shpFilePath : str
        Rail forth shapefile path.
    idx : int
        Number of the observation (between 2 and 5).

    Returns
    -------
    None.

    """
    # Load rails als shapefile
    rail_forth = shapefile.Reader(shpFilePath)

    # Define figure
    px = 1/plt.rcParams['figure.dpi']
    fig, axs = plt.subplots(1, 2, figsize=(2000*px, 800*px))

    # Define Main set_title
    fig.suptitle(' Trajectoire numéro #%i' % idx,
                 backgroundcolor='blue',
                 color='white', fontsize=18)

    # -------------------------------------------------------------------------
    # SUBPLOT 122 : distance differences
    # -------------------------------------------------------------------------
    df_st2['timestamp'] = pd.to_datetime(df_st2['timestamp'],
                                         format='%H:%M:s')
    axs[0].scatter(df_st2['timestamp'], delta)
    # plt.xticks(rotation = 45)

    # Labels
    axs[0].set_ylabel('$\Delta$ écarts entre les théodolites [m]', fontsize=16)
    axs[0].set_xlabel('Temps', fontsize=16)
    axs[0].set_xticklabels(
        df_st2['timestamp'].dt.strftime('%H:%M'), rotation=45)

    # -------------------------------------------------------------------------
    # SUBPLOT 223 : Histogram of difference in distances
    # -------------------------------------------------------------------------
    n, bins, patches = axs[1].hist(delta, 'auto', facecolor='blue')

    # Labels
    axs[1].set_xlabel('$\Delta$ écarts entre les théodolites [m]', fontsize=16)
    axs[1].set_ylabel('Nombre d\'observations', fontsize=16)
    xlabels = df_st2['timestamp']

    # Set grid
    axs[1].grid(True)

    # Apply font size
    plt.rc('font', size=18)

    # Box / axis Limit
    _xmin = df_st2['lon'].min()-100
    _xmax = df_st2['lon'].max()+100
    _ymin = df_st2['lat'].min()-100
    _ymax = df_st2['lat'].max()+100

    plt.show()


def plotHist(d1a: object, d1b: object, idx1: int, d2a: object, d2b: object,
             idx2: int):
    """
    Plot 4 histogramm: dist with the ref. and dist between theo.

    Parameters
    ----------
    d1a : dataframe object
        Theodolite 'a' of the measure 'd1'.
    d1b : dataframe object
        Theodolite 'b' of the measure 'd1'.
    idx1 : int
        Number of the observation (between 2 and 5).
    d2a : dataframe object
        Theodolite 'b' of the measure 'd2'.
    d2b : dataframe object
        Theodolite 'b' of the measure 'd2'.
    idx2 : int
        Number of the observation (between 2 and 5).

    Returns
    -------
    None.

    """
    # Define figure
    fig, axs = plt.subplots(2, 2)
    # Define Main set_title
    fig.suptitle(' Histogrammes des distances avec la référence',
                 backgroundcolor='blue',
                 color='white')

    # X-axis label
    xtext = 'Distance entre les points du théodolite et la référence'
    ytext = 'Nombre d\'observations'
    # -------------------------------------------------------------------------
    # SUBPLOT 221 : Histogramm 1
    # -------------------------------------------------------------------------
    n, bins, patches = axs[0, 0].hist(
        d1a, 'auto', density=True, facecolor='blue')

    # Labels
    m = d1a.mean()
    m2 = d1a.median()
    s = d1a.std()

    axs[0, 0].set_xlabel(xtext)
    axs[0, 0].set_ylabel(ytext)
    axs[0, 0].set_title(
        'Théodolité #2, Trajectoire #%i, mean: %.3f, median: %.3f std: %.3f'
        % (idx1, m, m2, s))
    axs[0, 0].grid(True)

    # -------------------------------------------------------------------------
    # SUBPLOT 222 : Histogramm 2
    # -------------------------------------------------------------------------
    n, bins, patches = axs[0, 1].hist(
        d1b, 'auto', density=True, facecolor='blue')

    # Labels
    title = ''.join('Théodolité #2, Trajectoire #%i, mean: %.3f, median:',
                    ' %.3f, std: %.3f'
                    % (idx1, d1b.mean(), d1b.median(), d1b.std()))
    axs[0, 1].set_xlabel(xtext)
    axs[0, 1].set_ylabel(ytext)
    axs[0, 1].set_title(title)

    # Set Grid
    axs[0, 1].grid(True)

    # -------------------------------------------------------------------------
    # SUBPLOT 223 : Histogram 3
    # -------------------------------------------------------------------------
    n, bins, patches = axs[1, 0].hist(
        d2a, 'auto', density=True, facecolor='blue')

    # Labels
    title = ''.join('Théodolite #1, Trajectoire #%i, mean: %.3f, median:',
                    '%.3f, std: %.3f'
                    % (idx2, d2a.mean(), d2a.median(), d2a.std()))
    axs[1, 0].set_xlabel(xtext)
    axs[1, 0].set_ylabel(ytext)
    axs[1, 0].set_title(title)

    # Set Grid
    axs[1, 0].grid(True)

    # -------------------------------------------------------------------------
    # SUBPLOT 224 : Histogram 4
    # -------------------------------------------------------------------------
    n, bins, patches = axs[1, 1].hist(
        d2b, 'auto', density=True, facecolor='blue')

    # Labels
    title = ''.join('Théodolité #2, Trajectoire #%i, mean: %.3f, median:',
                    '%.3f, std: %.3f'
                    % (idx2, d2b.mean(), d2b.median(), d2b.std()))
    axs[1, 1].set_xlabel(xtext)
    axs[1, 1].set_ylabel(ytext)
    axs[1, 1].set_title(title)

    # Set Grid on
    axs[1, 1].grid(True)
    plt.show()


def plotHist2(d1a: object, d1b: object, idx1: int):
    """
    Plot Histogramm of of dist. between theodolites and references pro series.

    Parameters
    ----------
    d1a : dataframe object
        Theodolite 'a' of the measure 'd1'.
    d1b : dataframe object
        Theodolite 'b' of the measure 'd1'.
    idx1 : int
        Number of the observation (between 2 and 5).

    Returns
    -------
    None.

    """
    # Define figure
    px = 1/plt.rcParams['figure.dpi']
    fig, axs = plt.subplots(1, 2, figsize=(2000*px, 800*px))

    # Statistics
    m = d1a.mean()
    m2 = d1a.median()
    s = d1a.std()

    # Label text
    xtext = 'Distance entre les points du théodolite et la référence [m]'
    ytext = 'Nombre d\'observations'

    # -------------------------------------------------------------------------
    # SUBPLOT 221 : Histogramm 1
    # -------------------------------------------------------------------------
    n, bins, patches = axs[0].hist(d1a, 'auto', density=True, facecolor='blue')

    # Labels
    title = ''.join('Théodolité #1, Trajectoire #%i,\n$\mu$: %.3f, ',
                    'median: %.3f $\sigma$: %.3f' % (idx1, m, m2, s))
    axs[0].set_xlabel(xtext)
    axs[0].set_ylabel(ytext)
    axs[0].set_title(title)

    # Set x-label font size
    plt.xticks(fontsize=16)

    # Set Grid
    axs[0].grid(True)

    # -------------------------------------------------------------------------
    # SUBPLOT 222 : Histogramm 2
    # -------------------------------------------------------------------------
    n, bins, patches = axs[1].hist(d1b, 'auto', density=True, facecolor='blue')

    # Labels
    title = ''.join('Théodolité #2, Trajectoire #%i, \n$\mu$: %.3f, ',
                    'median: %.3f, $\sigma$: %.3f'
                    % (idx1, d1b.mean(), d1b.median(), d1b.std()))
    axs[1].set_xlabel(xtext)
    axs[1].set_ylabel(ytext)
    axs[1].set_title(title)

    # Set Grid on
    axs[1].grid(True)

    # Set x-label font size
    plt.rc('font', size=18)

    plt.show()


def plotShpLine(shp1: str, shp2: str, df: object, df1: object, df2: object,
                df3: object):
    """
    PLot references shapelines and the 3 receivers points measures.

    Parameters
    ----------
    shp1 : str
        File path of rail forth.
    shp2 : str
        File path of rail back.
    df : object
        data of the thodolites.
    df1 : object
        Trimble NetR9 data.
    df2 : object
        data of the u-blox ZED-F9P receiver with swipos correction.
    df3 : object
        data of the u-blox ZED-F9P receiver with SAPA correction..

    Returns
    -------
    None.

    """
    # Load rails als shapefile
    shp1 = shapefile.Reader(shp1)
    shp2 = shapefile.Reader(shp2)

    # Observations des swipos
    plt.scatter(df['lon'], df['lat'], label='théodolite')
    plt.scatter(df1['lon'], df1['lat'], label='netr9')
    plt.scatter(df2['lon'], df2['lat'], label='ublox swipos')
    plt.scatter(df3['lon'], df3['lat'], label='ublox sapcorda')

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

    plt.xlim([_xmin, _xmax])
    plt.ylim([_ymin, _ymax])
    plt.legend()
    plt.show()


def plotRefLine(theo_shp_path1: str, theo_shp_path2: str, rail_shp_path: str,
                df: object, df2: object):
    """
    Plot the reference line of the rails, as the tho measures and their traces.

    Parameters
    ----------
    theo_shp_path1 : str
        File path to the shape file with the trace of the measures of the
        first theodolite.
    theo_shp_path2 : str
        File path to the shape file with the trace of the measures of the
        second theodolite.
    rail_shp_path : str
        Path to the shape file of the rail line reference.
    df : object
        Dataframe with the observation of the first theodolites.
    df2 : object
        Dataframe with the observation of the second theodolites.

    Returns
    -------
    None.

    """
    # Load rails als shapefile
    shp1 = shapefile.Reader(theo_shp_path1)
    shp2 = shapefile.Reader(theo_shp_path2)
    rail = shapefile.Reader(rail_shp_path)

    plt.scatter(df['lon'], df['lat'])
    plt.scatter(df2['lon'], df2['lat'])

    for shape in shp1.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y, label='Théodolite 1')
    for shape in shp2.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y, label='Théodolite 2')

    for shape in rail.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y)

    # Box / axis Limit
    _xmin = df['lon'].min()-100
    _xmax = df['lon'].max()+100
    _ymin = df['lat'].min()-100
    _ymax = df['lat'].max()+100

    plt.xlim([_xmin, _xmax])
    plt.ylim([_ymin, _ymax])
    plt.legend()
    plt.show()
