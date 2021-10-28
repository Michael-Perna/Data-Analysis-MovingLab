# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 15:31:00 2021

@author: Michael
"""
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd


def plotHistAcc(dist, bins, weights, CDF, quantile, receiver, do_xlim):
    # Plot Histogtam
    print('Plottining Accuracy Histogram')
    px = 1/plt.rcParams['figure.dpi']
    fig, ax = plt.subplots(figsize=(1000*px, 500*px))
    # Plot PDF
    ax.hist(dist,
            bins=bins,
            weights=weights,
            edgecolor='black',
            color='blue',
            label='PDF')
    # Plot CDF
    CDF = np.append([0], CDF)
    ax.plot(bins,
            CDF,
            color='red',
            label='CDF')

    # Plot   Quantiles
    for x, y in zip(quantile, [0.5, 0.75, 0.9]):
        ax.plot([x, x], [0, y],
                color='orange', linestyle='--')

        ax.plot([0, x], [y, y],
                color='orange', linestyle='--')
        # Add text label on y axis
        # plt.text(x,0,'%.00f'%x,rotation=90)

    # Axes apparence
    # tick= np.sort(np.append(quantile.round(decimals=2),np.arange(0.5, int(max(dist)), 0.5)))
    # tick = tick[tick!=3]
    # ax.set_xticks(tick)
    ax.set_yticks([0.05, 0.25, 0.5, 0.75, 0.9])
    if do_xlim:
        xlim = quantile[2] + 1
        tick = np.sort(np.append(quantile.round(decimals=2),
                       np.arange(0.5, int(xlim), 0.5)))
        ax.set_xticks(tick)
        ax.set_xlim(0, xlim)
    # Ax attributes
    ax.legend()
    ax.set_title('Récépeteur %s' % receiver,
                 backgroundcolor='blue',
                 color='white')
    ax.set_xlabel('Erreur de Position Horizontal [m]')
    ax.set_ylabel('Probabilité')
    ax.text(0.8, 0.7, 'Nombre d\'époques : %i \néquivalent à : %.0f de jours de navigations' % (
        len(dist), len(dist)/3600/24))

    # # Save Figure
    # if fname[0]:
    #     # Get distance form rail and save each tracks
    #     root, tail = os.path.split(fname[1])
    #     if not os.path.isdir(root):
    #         os.makedirs(root)
    #         print("Created folder : ", root)
    #     fig.savefig(fname[1], dpi=1000)


def plotHistAcc2(dist, bins, weights, CDF, quantile, receiver, color1,
                 dist2, bins2, weights2, CDF2, quantile2, fname, receiver2, color2, do_xlim):
    # Plot Histogtam
    print('Plottining Accuracy Histogram')
    px = 1/plt.rcParams['figure.dpi']
    fig, ax = plt.subplots(figsize=(1000*px, 500*px))
    # Plot PDF
    ax.hist(dist,
            bins=bins,
            weights=weights,
            edgecolor='black',
            color=color1,
            label='PDF %s' % receiver,
            alpha=0.7)
    # Plot CDF
    CDF = np.append([0], CDF)
    ax.plot(bins,
            CDF,
            color=color1,
            label='CDF %s' % receiver)

    # Plot PDF
    ax.hist(dist2,
            bins=bins2,
            weights=weights2,
            edgecolor='black',
            color=color2,
            label='PDF %s' % receiver2,
            alpha=0.7)
    # Plot CDF
    CDF2 = np.append([0], CDF2)
    ax.plot(bins2,
            CDF2,
            color=color2,
            label='CDF %s' % receiver2)

    # Plot   Quantiles
    for x, y in zip(quantile, [0.5, 0.75, 0.9]):
        ax.plot([x, x], [0, y],
                color=color1, linestyle='--')

        ax.plot([0, x], [y, y],
                color=color1, linestyle='-.')
        # Add text label on y axis
        # plt.text(x,0,'%.00f'%x,rotation=90)

    # Plot   Quantiles
    for x, y in zip(quantile2, [0.5, 0.75, 0.9]):
        ax.plot([x, x], [0, y],
                color=color2, linestyle='--')

        ax.plot([0, x], [y, y],
                color=color2, linestyle='--')
        # Add text label on y axis
        # plt.text(x,0,'%.00f'%x,rotation=90)

    # Axes apparence

    ax.set_yticks([0.05, 0.25, 0.5, 0.75, 0.9])
    if do_xlim:
        xlim1 = quantile[2] + 1
        xlim2 = quantile2[2] + 1
        xlim = max(xlim1, xlim2)
        tick = np.sort(np.arange(0.5, int(xlim), 0.5))
        ax.set_xticks(tick)
        ax.set_xlim(0, xlim)

    # Quantile Values
    q1 = quantile.round(decimals=2).tolist()
    q2 = quantile2.round(decimals=2).tolist()
    for x1, x2 in zip(q1, q2):
        ax.text(x1, -0.04, str(x1), color=color1,
                rotation=30,
                rotation_mode='anchor',
                horizontalalignment='right',
                verticalalignment='baseline',
                fontweight='bold',
                fontstretch='extra-condensed')
        ax.text(x2, -0.08, str(x2), color=color2,
                rotation=30,
                rotation_mode='anchor',
                horizontalalignment='right',
                verticalalignment='baseline',
                fontweight='bold',

                fontstretch='extra-condensed')
    ax.text(3.5, 0.5, 'Récepteur : {} \nNombre d\'époques : {} \néquivalent à : {} d\'heures de navigations\n\n\nRécepteur : {} \nNombre d\'époques : {} \néquivalent à : {} d\'heures de navigations'.format(receiver, len(dist), int(len(dist)/3600), receiver2, len(dist2), int(len(dist2)/3600)),
            fontsize=18)
    plt.rc('font', size=18)

    # Ax attributes
    ax.legend()
    ax.set_title('Récépeteur %s & %s' % (receiver, receiver2),
                 backgroundcolor='blue',
                 fontsize=18,
                 color='white')
    label = ax.set_xlabel('Erreur de Position Horizontal [m]',
                          fontsize=16)

    # ax.xaxis.set_label_coords(1, -0.9)
    ax.set_ylabel('Probabilité',
                  fontsize=16)

    # Save Figure
    if fname[0]:
        # Get distance form rail and save each tracks
        root, tail = os.path.split(fname[1])
        if not os.path.isdir(root):
            os.makedirs(root)
            print("Created folder : ", root)
        fig.savefig(fname[1], dpi=1000)


def plot_HPE(df, df2, df3, receiver, receiver2, receiver3, posMode, posMode2, posMode3):

    # PLOT 1
    fig, ax = plt.subplots()

    df4 = df3.assign(y1=df.dist, y2=df2.dist, y3=df3.dist)
    df4.reset_index(drop=True)

    ax.plot(range(len(df4.timestamp)), df4.y3,
            color='red',
            label='NetR9 avec swipos RTK-VRS',
            linewidth=0.5)
    ax.plot(range(len(df4.timestamp)), df4.y2,
            color='orange',
            label='u-blox ZED-F9P avec SAPOS PPP-RTK',
            linewidth=0.8)
    ax.plot(range(len(df4.timestamp)), df4.y1,
            color='blue',
            label='u-blox ZED-F9P avec swispos RTK-VRS',
            linewidth=0.8)

    # Axes tick
    xtick = np.arange(0, len(df4.timestamp), 3600*24*4)
    ax.set_xticks(xtick)
    xlabels = df4.iloc[xtick]['timestamp'].dt.strftime('%d/%m/%Y')
    ax.set_xticklabels(xlabels, fontsize=16)  # , rotation=45)

    # Ax attributes
    ax.legend(loc='upper right', fontsize=16)
    ax.set_title('Erreurs de postionnement lateral', fontsize=18,
                 backgroundcolor='blue',
                 color='white')
    ax.set_ylabel('Erreur de Position Lateral [m]', fontsize=16)
    ax.set_xlabel('Date', fontsize=16, )
    ax.set_ylim(0, 50)
    ax.grid(which='both', axis='y')

    ax.text(3600, 44, 'Récepteur : {} $\mu$ {:.2f}m et $\sigma$: {:.2f}m,\nRécepteur : {} $\mu$ {:.2f}m et $\sigma$ {:.2f}m,\nRécepteur : {} $\mu$ {:.2f}m et $\sigma$ {:.2f}m'.format(receiver, posMode['mean'], posMode['std'], receiver2, posMode2['mean'], posMode2['std'], receiver3, posMode3['mean'], posMode3['std']), fontsize=18,
            backgroundcolor='white')
    plt.rc('font', size=18)

    # PLOT 2
    fig, ax = plt.subplots()

    df5 = df2.assign(y1=df.dist, y2=df2.dist)
    df5.reset_index(drop=True)

    ax.plot(range(len(df5.dist)), df5.y2,
            label='u-blox ZED-F9P avec SAPOS PPP-RTK',
            color='orange', linewidth=0.8)
    ax.plot(range(len(df5.dist)), df5.y1,
            label='u-blox ZED-F9P avec swispos RTK-VRS',
            color='blue',  # alpha = 0.5,
            linewidth=0.5)

    # Axes tick
    xtick = np.arange(0, len(df5.timestamp), 3600*24)
    ax.set_xticks(xtick)
    xlabels = df5.iloc[xtick]['timestamp'].dt.strftime('%d/%m/%Y')
    ax.set_xticklabels(xlabels, rotation=20, fontsize=16)

    # Ax attributes
    ax.legend(loc='upper right', fontsize=16)
    ax.set_title('Erreurs de postionnement lateral', fontsize=18,
                 backgroundcolor='blue',
                 color='white')
    ax.set_ylabel('Erreur de Position Lateral [m]', fontsize=16)
    ax.set_xlabel(
        'Ensemble des époques sans intéruptions [s] ', fontsize=16)
    ax.set_ylim(0, 8)
    ax.grid(which='both', axis='y')

    ax.text(0, 7, 'Récepteur : {} $\mu$ {:.2f}m et $\sigma$: {:.2f}m,\nRécepteur : {} $\mu$ {:.2f}m et $\sigma$ {:.2f}m,'.format(
        receiver, posMode['mean'], posMode['std'], receiver2, posMode2['mean'], posMode2['std']), fontsize=18, backgroundcolor='white')

    plt.rc('font', size=18)

    # PLOT 3 - ZOOM
    fig, ax = plt.subplots()

    df5 = df2.assign(y1=df.dist, y2=df2.dist)
    df5.reset_index(drop=True)

    ax.plot(range(len(df5.dist)), df5.y2,
            label='u-blox ZED-F9P avec SAPOS PPP-RTK',
            color='orange', linewidth=0.8)
    ax.plot(range(len(df5.dist)), df5.y1,
            label='u-blox ZED-F9P avec swipos RTK-VRS',
            color='blue',  # alpha = 0.5,
            linewidth=0.5)

    # Axes tick
    xtick = np.arange(0, len(df5.timestamp), 2*3600)
    ax.set_xticks(xtick)
    xlabels = df5.iloc[xtick]['timestamp'].dt.strftime('%d/%m/%Y - %H:%M')
    ax.set_xticklabels(xlabels, fontsize=16, rotation=20)

    # Ax attributes
    ax.legend(loc='upper left', fontsize=16)
    ax.set_title('Erreurs de postionnement lateral - Agrandi', fontsize=20,
                 backgroundcolor='blue',
                 color='white')
    ax.set_ylabel('Erreur de Position Lateral [m]', fontsize=18)
    ax.set_xlabel(' Date ', fontsize=18)
    ax.set_ylim(0, 8)

    ax.grid(which='both', axis='y')

    plt.rc('font', size=18)
    plt.rc('font', size=18)
