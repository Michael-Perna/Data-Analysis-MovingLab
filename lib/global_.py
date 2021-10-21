#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 11 11:31:51 2021.

@author: michael
"""


# =============================================================================
# ITRF14 to CHTRF95 drift for the 2021 year
# =============================================================================
drift2021 = [['2020-12-31', 0.492, -0.509, -0.382],
             ['2021-01-31', 0.493, -0.511, -0.383],
             ['2021-02-28', 0.495, -0.512, -0.384],
             ['2021-03-31', 0.496, -0.514, -0.385],
             ['2021-04-30', 0.497, -0.515, -0.386],
             ['2021-05-31', 0.498, -0.517, -0.387],
             ['2021-06-30', 0.499, -0.518, -0.388],
             ['2021-07-31', 0.500, -0.520, -0.389],
             ['2021-08-31', 0.501, -0.521, -0.390],
             ['2021-09-30', 0.503, -0.523, -0.391],
             ['2021-10-31', 0.504, -0.524, -0.392],
             ['2021-11-30', 0.505, -0.526, -0.393],
             ['2021-12-31', 0.506, -0.527, -0.394]]


# =============================================================================
# GNSS Dictionnaries
# =============================================================================
qualityFlag = {0: 'Missing',
               1: 'No Fix',
               2: 'Autonomous GNSS fix',
               3: 'Differential GNSS fix',
               4: 'RTK fixed',
               5: 'RTK float',
               6: 'Estimated or dead reckoning fix'
               }

navModeFlag = {1: 'No Fix',
               2: '2D fix',
               3: '3D fix',
               }

fixType = {0: 'No Fix',
           1: 'Dead Reckoning only',
           2: '2D fix',
           3: '3D fix',
           4: 'GNSS + dead reckoning',
           5: 'Time only fix',
           6: 'Reserved channel'
           }

# =============================================================================
# GNSS Receivers: brute observations
# =============================================================================
header1 = ['timestamp',
           'lon',
           'stdLong',
           'lat',
           'stdLat',
           'alt',
           'stdAlt',
           'sep',
           'rangeRMS',
           'posMode',
           'numSV',
           'difAge',
           'numGP',
           'numGL',
           'numGA',
           'numGB',
           'opMode',
           'navMode',
           'PDOP',
           'HDOP',
           'VDOP',
           'stdMajor',
           'stdMinor',
           'orient'
           ]

types1 = {'timestamp': str,
          'lon': float,
          'stdLong': float,
          'lat': float,
          'stdLat': float,
          'alt': float,
          'stdAlt': float,
          'sep': float,
          'rangeRMS': float,
          'posMode': int,
          'numSV': float,
          'difAge': float,
          'numGP': int,
          'numGL': int,
          'numGA': int,
          'numGB': int,
          'opMode': int,
          'navMode': int,
          'PDOP': float,
          'HDOP': float,
          'VDOP': float,
          'stdMajor': float,
          'stdMinor': float,
          'orient': float
          }

# =============================================================================
# GNSS receiver: after analysis
# =============================================================================
header2 = ['timestamp',
           'lon',
           'stdLong',
           'lat',
           'stdLat',
           'alt',
           'stdAlt',
           'sep',
           'rangeRMS',
           'posMode',
           'numSV',
           'difAge',
           'numGP',
           'numGL',
           'numGA',
           'numGB',
           'opMode',
           'navMode',
           'PDOP',
           'HDOP',
           'VDOP',
           'stdMajor',
           'stdMinor',
           'orient',
           'geometry',
           'dist',
           'pproj',
           'err',
           'Sytram',
           'Smax'
           ]

types2 = {'timestamp': str,
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
          'numGP': int,
          'numGL': int,
          'numGA': int,
          'numGB': int,
          'opMode': str,
          'navMode': str,
          'PDOP': float,
          'HDOP': float,
          'VDOP': float,
          'stdMajor': float,
          'stdMinor': float,
          'orient': float,
          'geometry': float,
          'dist': float,
          'pproj': float,
          'err': float,
          'Sytram': float,
          'Smax': float
          }

# =============================================================================
# xsens receiver: brute observations
# =============================================================================

header3 = ['timestamp',
           'lon',
           'stdLong',
           'lat',
           'stdLat',
           'alt',
           'stdAlt',
           'sep',
           'numSV',
           'PDOP',
           'HDOP',
           'VDOP',
           'fixType'
           ]

types3 = {'timestamp': str,
          'lon': float,
          'stdLong': float,
          'lat': float,
          'stdLat': float,
          'alt': float,
          'stdAlt': float,
          'sep': float,
          'numSV': float,
          'PDOP': float,
          'HDOP': float,
          'VDOP': float,
          'fixtype': str
          }

header4 = ['PacketCounter',
           'UTC_Nano',
           'UTC_Year',
           'UTC_Month',
           'UTC_Day',
           'UTC_Hour',
           'UTC_Minute',
           'UTC_Second',
           'UTC_Valid',
           'StatusWord',
           'Latitude',
           'Longitude',
           'Altitude',
           'NUTimeOfWeek',
           'TimeAccuracyEst',
           'GNSSNanoSecOfSec',
           'GNSSYear',
           'GNSSMonth',
           'GNSSDay',
           'GNSSHour',
           'GNSSMin',
           'GNSSSec',
           'GNSSTimeValidity',
           'GNSSFixtype',
           'GNSSFixStatusFlags',
           'NumberOfSV',
           'Longitude',
           'Latitude',
           'Height',
           'HeightMeanSeaLevel',
           'HorizontalAccuracyEst',
           'VerticalAccuracyEst',
           'VelocityN',
           'VelocityE',
           'VelocityD',
           'GroundSpeed',
           'MotionHeading',
           'SpeedAccuracyEst',
           'HeadingAccurayEst',
           'Heading',
           'GeometricDOP',
           'PositionDOP',
           'TimeDOP',
           'VerticalDOP',
           'HorizontalDOP',
           'NorthingDOP',
           'EastingDOP',
           'NSVTimeOfWeek',
           'GnssId[0]',
           'SvId[0]',
           'Cno[0]',
           'Flags[0]',
           'GnssId[1]',
           'SvId[1]',
           'Cno[1]',
           'Flags[1]',
           'GnssId[2]',
           'SvId[2]',
           'Cno[2]',
           'Flags[2]',
           'GnssId[3]',
           'SvId[3]',
           'Cno[3]',
           'Flags[3]',
           'GnssId[4]',
           'SvId[4]',
           'Cno[4]',
           'Flags[4]',
           'GnssId[5]',
           'SvId[5]',
           'Cno[5]',
           'Flags[5]',
           'GnssId[6]',
           'SvId[6]',
           'Cno[6]',
           'Flags[6]',
           'GnssId[7]',
           'SvId[7]',
           'Cno[7]',
           'Flags[7]',
           'GnssId[8]',
           'SvId[8]',
           'Cno[8]',
           'Flags[8]',
           'GnssId[9]',
           'SvId[9]',
           'Cno[9]',
           'Flags[9]',
           'GnssId[10]',
           'SvId[10]',
           'Cno[10]',
           'Flags[10]',
           'GnssId[11]',
           'SvId[11]',
           'Cno[11]',
           'Flags[11]',
           'GnssId[12]',
           'SvId[12]',
           'Cno[12]',
           'Flags[12]',
           'GnssId[13]',
           'SvId[13]',
           'Cno[13]',
           'Flags[13]',
           'GnssId[14]',
           'SvId[14]',
           'Cno[14]',
           'Flags[14]',
           'GnssId[15]',
           'SvId[15]',
           'Cno[15]',
           'Flags[15]',
           'GnssId[16]',
           'SvId[16]',
           'Cno[16]',
           'Flags[16]',
           'GnssId[17]',
           'SvId[17]',
           'Cno[17]',
           'Flags[17]',
           'GnssId[18]',
           'SvId[18]',
           'Cno[18]',
           'Flags[18]',
           'GnssId[19]',
           'SvId[19]',
           'Cno[19]',
           'Flags[19]',
           'GnssId[20]',
           'SvId[20]',
           'Cno[20]',
           'Flags[20]',
           'GnssId[21]',
           'SvId[21]',
           'Cno[21]',
           'Flags[21]',
           'GnssId[22]',
           'SvId[22]',
           'Cno[22]',
           'Flags[22]',
           'GnssId[23]',
           'SvId[23]',
           'Cno[23]',
           'Flags[23]',
           'GnssId[24]',
           'SvId[24]',
           'Cno[24]',
           'Flags[24]',
           'GnssId[25]',
           'SvId[25]',
           'Cno[25]',
           'Flags[25]',
           'GnssId[26]',
           'SvId[26]',
           'Cno[26]',
           'Flags[26]',
           'GnssId[27]',
           'SvId[27]',
           'Cno[27]'
           'Flags[27]',
           'GnssId[28]',
           'vId[28]',
           'Cno[28]',
           'Flags[28]',
           'GnssId[29]',
           'SvId[29]',
           'Cno[29]',
           'Flags[29]',
           'GnssId[30]',
           'SvId[30]',
           'Cno[30]',
           'Flags[30]',
           'GnssId[31]',
           'SvId[31]',
           'Cno[31]',
           'Flags[31]',
           'GnssId[32]',
           'SvId[32]',
           'Cno[32]',
           'Flags[32]',
           'GnssId[33]',
           'SvId[33]',
           'Cno[33]',
           'Flags[33]',
           'GnssId[34]',
           'SvId[34]',
           'Cno[34]',
           'Flags[34]',
           'GnssId[35]',
           'SvId[35]',
           'Cno[35]',
           'Flags[35]',
           'GnssId[36]',
           'SvId[36]',
           'Cno[36]',
           'Flags[36]',
           'GnssId[37]',
           'SvId[37]',
           'Cno[37]',
           'Flags[37]',
           'GnssId[38]',
           'SvId[38]',
           'Cno[38]',
           'Flags[38]',
           'GnssId[39]',
           'SvId[39]',
           'Cno[39]',
           'Flags[39]',
           'GnssId[40]',
           'SvId[40]',
           'Cno[40]',
           'Flags[40]',
           'GnssId[41]',
           'SvId[41]',
           'Cno[41]',
           'Flags[41]',
           'GnssId[42]',
           'SvId[42]',
           'Cno[42]',
           'Flags[42]',
           'GnssId[43]',
           'SvId[43]',
           'Cno[43]',
           'Flags[43]',
           'GnssId[44]',
           'SvId[44]',
           'Cno[44]',
           'Flags[44]',
           'GnssId[45]',
           'SvId[45]',
           'Cno[45]',
           'Flags[45]',
           'GnssId[46]',
           'SvId[46]',
           'Cno[46]',
           'Flags[46]',
           'GnssId[47]',
           'SvId[47]',
           'Cno[47]',
           'Flags[47]',
           'GnssId[48]',
           'SvId[48]',
           'Cno[48]',
           'Flags[48]',
           'GnssId[49]',
           'SvId[49]',
           'Cno[49]',
           'Flags[49]',
           'GnssId[50]',
           'SvId[50]',
           'Cno[50]',
           'Flags[50]',
           'GnssId[51]',
           'SvId[51]',
           'Cno[51]',
           'Flags[51]',
           'GnssId[52]',
           'SvId[52]',
           'Cno[52]',
           'Flags[52]',
           'GnssId[53]',
           'SvId[53]',
           'Cno[53]',
           'Flags[53]',
           'GnssId[54]',
           'SvId[54]',
           'Cno[54]',
           'Flags[54]',
           'GnssId[55]',
           'SvId[55]',
           'Cno[55]',
           'Flags[55]',
           'GnssId[56]',
           'SvId[56]',
           'Cno[56]',
           'Flags[56]',
           'GnssId[57]',
           'SvId[57]',
           'Cno[57]',
           'Flags[57]',
           'GnssId[58]',
           'SvId[58]',
           'Cno[58]',
           'Flags[58]',
           'GnssId[59]',
           'SvId[59]',
           'Cno[59]',
           'Flags[59]'
           ]


# =============================================================================
# Theodolites
# =============================================================================
header5 = ['Julian Date',
           'Day',
           'Month',
           'Year',
           'Hour',
           'Minute',
           'Second',
           'lon',
           'lat',
           'alt',
           ]

types5 = {'Julian Date': str,
          'Day': str,
          'Month': str,
          'Year': str,
          'Hour': str,
          'Minute': str,
          'Second': str,
          'lon': float,
          'lat': float,
          'alt': float
          }
