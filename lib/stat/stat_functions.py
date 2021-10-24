# -*- coding: utf-8 -*-

import numpy as np


def pdf_cdf(df):
    # Drop epochs with no positions or inf position
    df['dist'].replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df['dist'].dropna()
    dist = df.to_numpy()

    # Get Quantile
    quantile = np.nanquantile(dist,
                              [0.5, 0.75, 0.9],
                              keepdims=False)
    # Define bins sequence
    bins = np.append(np.arange(0, 20, 0.01), np.arange(20, max(dist), 1))

    # Get counts from numpy.histogram
    counts, bins = np.histogram(dist, bins=bins)

    # Probability Density Function :
    N = sum(counts)
    PDF = counts/N
    weights = np.ones_like(dist)/N  # Used to normalized the histogram

    # Cumulative Densitive Function
    CDF = np.cumsum(PDF)

    return dist, bins, weights, CDF, quantile
