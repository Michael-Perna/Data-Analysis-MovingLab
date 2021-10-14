# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 17:07:52 2020.

@author: Michael
"""
import pandas as pd
from itertools import permutations, chain
from . import global_
from . import timetools


def _six_str(letter: str, n_string: int):
    """
    Create 'n_string' with ascendent consecuitve 'letter'.

    Parameters
    ----------
    letter : str
        Should be a single letter.
    n_string : integer
        Number of wanted output string.

    Returns
    -------
    letters : list
        The list contain all the created string.

    Example:
        _six_str('A', 3)
        letters = 'A', 'AA', 'AAA'
    """
    let = letter
    letters = ['']*n_string
    for i in range(n_string):
        letters[i] = letter
        letter = letter + let
    return letters


def _pos_dict():
    """Make dictionnary with all letter permutation."""
    NoFix = _six_str('N', 6)

    AutoFix = _six_str('A', 6)
    a = [''.join(p) for p in permutations('ANNNNN')]
    b = [''.join(p) for p in permutations('AANNNN')]
    c = [''.join(p) for p in permutations('AAANNN')]
    d = [''.join(p) for p in permutations('AAAANN')]
    e = [''.join(p) for p in permutations('AAAAAN')]
    f = [''.join(p) for p in permutations('ANNN')]
    g = [''.join(p) for p in permutations('AANN')]
    h = [''.join(p) for p in permutations('AAAN')]
    AutoFix = list(chain(AutoFix, a, b, c, d, e, f, g, h))

    DiffFix = _six_str('D', 6)
    a = [''.join(p) for p in permutations('DNNNNN')]
    b = [''.join(p) for p in permutations('DDNNNN')]
    c = [''.join(p) for p in permutations('DDDNNN')]
    d = [''.join(p) for p in permutations('DDDDNN')]
    e = [''.join(p) for p in permutations('DDDDDN')]
    f = [''.join(p) for p in permutations('DNNN')]
    g = [''.join(p) for p in permutations('DDNN')]
    h = [''.join(p) for p in permutations('DDDN')]
    DiffFix = list(chain(DiffFix, a, b, c, d, e, f, g, h))

    RtkFloat = _six_str('F', 6)
    a = [''.join(p) for p in permutations('FNNNNN')]
    b = [''.join(p) for p in permutations('FFNNNN')]
    c = [''.join(p) for p in permutations('FFFNNN')]
    d = [''.join(p) for p in permutations('FFFFNN')]
    e = [''.join(p) for p in permutations('FFFFFN')]
    f = [''.join(p) for p in permutations('FNNN')]
    g = [''.join(p) for p in permutations('FFNN')]
    h = [''.join(p) for p in permutations('FFFN')]
    RtkFloat = list(chain(RtkFloat, a, b, c, d, e, f, g, h))

    RtkFix = _six_str('R', 6)
    a = [''.join(p) for p in permutations('RNNNNN')]
    b = [''.join(p) for p in permutations('RRNNNN')]
    c = [''.join(p) for p in permutations('RRRNNN')]
    d = [''.join(p) for p in permutations('RRRRNN')]
    e = [''.join(p) for p in permutations('RRRRRN')]
    f = [''.join(p) for p in permutations('RNNN')]
    g = [''.join(p) for p in permutations('RRNN')]
    h = [''.join(p) for p in permutations('RRRN')]
    RtkFix = list(chain(RtkFix, a, b, c, d, e, f, g, h))

    # Creating an e,pty dictionatry
    posMode = {}

    # Adding lis as value
    posMode['No Fix'] = ''
    posMode['No Fix'] = NoFix
    posMode['Autonomous GNSS fix'] = AutoFix
    posMode['Differential GNSS fix'] = DiffFix
    posMode['RTK float'] = RtkFloat
    posMode['RTK fixed'] = RtkFix

    return posMode


def _import_df(filename: str, header: dict, types: dict, dateFormat: str,
               utf8 = True):
    """
    Import dataframe from textfile.

    Parameters
    ----------
    filename : string
        file path to the data.
    header : dictionnary
        name of the column to be assinged to the dataframe df.
    types : dictionnary
        type of the data of each column.
    dateFormat : string
        format to be applied to the timestamps string
        (i.e  '%Y-%m-%dT%H:%M:%SZ').
    utf8: boolean
        if 'True' : pd.read_csv(file, sep=',', header=None, dtype=str)
        if 'False': pd.read_csv(self.txt_file, sep='\t', skiprows=[1],
                         encoding='unicode_escape', dtype=str)

    Returns
    -------
    df : dataframe
        dataframe containig the column 'header' of the 'filename' file.
    valid : boolean
        False if the header does not much with the numbers of data columns.
        True otherwiser.

    """
    # Open the file
    file = open(filename)

    # Import csv file as DataFrame with pandas as String
    if utf8:
        df = pd.read_csv(file, sep=',', header=None, dtype=str)
    else:
        df = pd.read_csv(filename, sep='\t', skiprows=[1],
                         encoding='unicode_escape', dtype=str)

    # Getting shape of the df
    shape = df.shape
    # If the numbers of column missmatch return an error
    if shape[1] != len(header):
        valid = False
        return df, valid
    else:
        valid = True

    # Add name to each column
    df.columns = header

    # Apply the type format according to the dico
    for col, col_type in types.items():
        if col in df.columns:
            df[col] = df[col].astype(col_type, errors='ignore')

    # Apply time format
    if utf8:
        df['timestamp'] = pd.to_datetime(df['timestamp'],
                                         format=dateFormat)

    # Close the File
    file.close()

    return df, valid


def getFlag(df, navModeFlag, fixTypeFlag):
    """Assing string flag to parameter for more readability."""
    # Assing navigation mode flag (NMEA message)
    if 'navMode' in df.columns:
        df['navMode'] = df['navMode'].replace(navModeFlag)

    # Assing fix type flag (xsens message)
    if 'posMode' in df.columns:
        df['fixtype'] = df['fixtype'].replace(fixTypeFlag)

    # Assing position mode flag (NMEA message)
    if 'fixtype' in df.columns:
        posMode = _pos_dict()
        df['posMode'] = df['posMode'].replace(posMode['No Fix'], 'No Fix')
        df['posMode'] = df['posMode'].replace(
            posMode['Autonomous GNSS fix'], 'Autonomous GNSS fix'
            )
        df['posMode'] = df['posMode'].replace(
            posMode['Differential GNSS fix'], 'Differential GNSS fix'
            )
        df['posMode'] = df['posMode'].replace(
            posMode['RTK float'], 'RTK float'
            )
        df['posMode'] = df['posMode'].replace(
            posMode['RTK fixed'], 'RTK fixed'
        )
    return df


def nmea_df(filename):
    """
    Import .snmea data as dataframe and apply flag name to string flag.

    Returns
    -------
    df : dataframe
        dataframe containig the wnated parameters ('header') of the
        'filename' file.
    valid : boolean
        False if the header does not much with the numbers of data columns.
        True otherwiser.
    """
    dateFormat = '%Y-%m-%dT%H:%M:%SZ'

    global getFlag

    df, valid = _import_df(filename, header=global_.header1,
                           types=global_.types1, dateFormat=dateFormat)
    df = getFlag(df, navModeFlag=global_.navModeFlag,
                 fixTypeFlag=global_.qualityFlag)

    return df, valid


def result_df(filename, columns):
    """
    Import .results data as dataframe and apply flag name to string flag.

    Returns
    -------
    df : dataframe
        dataframe containig the wnated parameters ('header') of the
        'filename' file.
    valid : boolean
        False if the header does not much with the numbers of data columns.
        True otherwiser.
    """
    dateFormat = '%Y-%m-%d %H:%M:%S'

    df, valid = _import_df(filename, header=global_.header2,
                           types=global_.types2, dateFormat=dateFormat)

    # Select only column accordint to columns list
    if valid:
        df = df[columns]

    # Assing name to respective flag
    df = getFlag(df, navModeFlag=global_.navModeFlag,
                 fixTypeFlag=global_.qualityFlag)

    return df, valid


def stat_df(filename, columns):
    """
    Import .snmea data as dataframe and apply flag name to string flag.

    Returns
    -------
    df : dataframe
        dataframe containig the wnated parameters ('header') of the
        'filename' file.
    valid : boolean
        False if the header does not much with the numbers of data columns.
        True otherwiser.
    """
    dateFormat = '%Y-%m-%d %H:%M:%S'

    df, valid = _import_df(filename, header=columns,
                           types=global_.types2, dateFormat=dateFormat)

    return df, valid


# =============================================================================
# xsens
# =============================================================================
def xsense_df(filename, columns):
    """
    Import .results data as dataframe and apply flag name to string flag.

    Returns
    -------
    df : dataframe
        dataframe containig the wnated parameters ('header') of the
        'filename' file.
    valid : boolean
        False if the header does not much with the numbers of data columns.
        True otherwiser.
    """
    dateFormat = '%Y-%m-%dT%H:%M:%S.%fZ'
    df, valid = _import_df(filename, header=global_.header3,
                           types=global_.types3, dateFormat=dateFormat)

    # Select only column accordint to columns list
    if valid:
        df = df[columns]

    # Assing name to respective flag
    df = getFlag(df, navModeFlag=global_.navModeFlag,
                 fixTypeFlag=global_.qualityFlag)

    return df, valid


# =============================================================================
# Theodolites
# =============================================================================
def theo_df(filename: str, columns: list):
    """
    Import results data as dataframe and apply flag name to string flag.

    Returns
    -------
    df : dataframe
        dataframe containig the wnated parameters ('header') of the
        'filename' file.
    valid : boolean
        False if the header does not much with the numbers of data columns.
        True otherwiser.
    """
    dateFormat = '%Y-%m-%dT%H:%M:%S.%fZ'
    df, valid = _import_df(filename, header=global_.header5,
                           types=global_.types5, dateFormat=dateFormat,
                           utf8=False)

    # Convert UTC date into utcrcf3339 standard
    df['date'] = df['Year'] + df['Month'].str.zfill(2) +\
        df['Day'].str.zfill(2) + 'T' + \
        df['Hour'].str.zfill(2) +\
        df['Minute'].str.zfill(2) + df['Second']

    df['timestamp'] = df['date'].map(lambda x: timetools.utcrcf3339(x))

    # Select only column accordint to columns list
    if valid:
        df = df[columns]

    # Assing name to respective flag
    df = getFlag(df, navModeFlag=global_.navModeFlag,
                 fixTypeFlag=global_.qualityFlag)

    return df, valid

    # # Create Data Frame
    # columns = global_.header3

    # df_out = pd.DataFrame(
    #     data=None, index=None, columns=columns, dtype=None, copy=False)


    # # Open txt file
    # df = pd.read_csv(self.txt_file, sep='\t', skiprows=[1],
    #                  encoding='unicode_escape', dtype=str)

    # # Convert UTC date into utcrcf3339 standard
    # df['date'] = df['Year'] + df['Month'].str.zfill(2) +\
    #     df['Day'].str.zfill(2) + 'T' + \
    #     df['Hour'].str.zfill(2) +\
    #     df['Minute'].str.zfill(2) + df['Second']

    # df['timestamp'] = df['date'].map(lambda x: timetools.utcrcf3339(x))

    # df = geolib.distance_df2shpfile(df, shpfile=self.shpfile,
    #                                 x='East', y='North')

    # # Fill output
    # df_out['timestamp'] = df['timestamp']
    # df_out['lon'] = df['East']
    # .df_out['lat'] = df['North']
    # self.df_out['alt'] = df['Altitude']
    # self.df_out['dist'] = df['dist']

    # return self.df_out
