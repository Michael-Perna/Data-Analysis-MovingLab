# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 17:07:52 2020

@author: Michael
"""
import pandas as pd
from itertools import permutations, chain


def six_str(letter, length):
    l = letter
    letters=['']*length
    for i in range(length):
        letters[i]= letter
        letter = letter + l
    return letters

def _pos_dict():
    NoFix = six_str('N',6)

    AutoFix = six_str('A',6)
    a = [''.join(p) for p in permutations('ANNNNN')]
    b = [''.join(p) for p in permutations('AANNNN')]
    c = [''.join(p) for p in permutations('AAANNN')]
    d = [''.join(p) for p in permutations('AAAANN')]
    e = [''.join(p) for p in permutations('AAAAAN')]
    f = [''.join(p) for p in permutations('ANNN')]
    g = [''.join(p) for p in permutations('AANN')]
    h = [''.join(p) for p in permutations('AAAN')]
    AutoFix = list(chain(AutoFix,a,b,c,d,e,f,g,h))

    DiffFix = six_str('D',6)
    a = [''.join(p) for p in permutations('DNNNNN')]
    b = [''.join(p) for p in permutations('DDNNNN')]
    c = [''.join(p) for p in permutations('DDDNNN')]
    d = [''.join(p) for p in permutations('DDDDNN')]
    e = [''.join(p) for p in permutations('DDDDDN')]
    f = [''.join(p) for p in permutations('DNNN')]
    g = [''.join(p) for p in permutations('DDNN')]
    h = [''.join(p) for p in permutations('DDDN')]
    DiffFix = list(chain(DiffFix,a,b,c,d,e,f,g,h))

    RtkFloat = six_str('F',6)
    a = [''.join(p) for p in permutations('FNNNNN')]
    b = [''.join(p) for p in permutations('FFNNNN')]
    c = [''.join(p) for p in permutations('FFFNNN')]
    d = [''.join(p) for p in permutations('FFFFNN')]
    e = [''.join(p) for p in permutations('FFFFFN')]
    f = [''.join(p) for p in permutations('FNNN')]
    g = [''.join(p) for p in permutations('FFNN')]
    h = [''.join(p) for p in permutations('FFFN')]
    RtkFloat = list(chain(RtkFloat,a,b,c,d,e,f,g,h))

    RtkFix= six_str('R',6)
    a = [''.join(p) for p in permutations('RNNNNN')]
    b = [''.join(p) for p in permutations('RRNNNN')]
    c = [''.join(p) for p in permutations('RRRNNN')]
    d = [''.join(p) for p in permutations('RRRRNN')]
    e = [''.join(p) for p in permutations('RRRRRN')]
    f = [''.join(p) for p in permutations('RNNN')]
    g = [''.join(p) for p in permutations('RRNN')]
    h = [''.join(p) for p in permutations('RRRN')]
    RtkFix = list(chain(RtkFix,a,b,c,d,e,f,g,h))

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

def _import_df(filename, header, types, dateFormat, navModeFlag):
            # Open the file
        file = open(filename)

        # Import csv file as DataFrame with pandas as String
        df = pd.read_csv(file,
                         sep=',',
                         header=None,
                         dtype=str
                         )

        #Getting shape of the df
        shape = df.shape
        # If the numbers of column missmatch reurnt an error
        if shape[1]!= len(header):
            valid=False
            return df, valid
        else:
            valid=True
        # Add name to each column
        df.columns = header

        # Apply the type format according to the dico
        for col, col_type in types.items():
            if col in df.columns:
                df[col] = df[col].astype(col_type, errors='ignore')

        # Apply time format
        df['timestamp'] = pd.to_datetime(df['timestamp'],
                                         format=dateFormat)

        # Close the File
        file.close()



        return df, valid

qualityFlag = {0 :'Missing',
                1 :'No Fix',
                2 :'Autonomous GNSS fix',
                3 :'Differential GNSS fix',
                4 :'RTK fixed',
                5 :'RTK float',
                6 :'Estimated or dead reckoning fix'
                }

navModeFlag = {1 :'No Fix',
                2 :'2D fix',
                3 :'3D fix',
                }

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
            'orient']

types1 = {'timestamp':str,
            'lon':float,
            'stdLong':float,
            'lat':float,
            'stdLat':float,
            'alt':float,
            'stdAlt':float,
            'sep':float,
            'rangeRMS':float,
            'posMode':int,
            'numSV':float,
            'difAge': float,
            'numGP':int,
            'numGL':int,
            'numGA':int,
            'numGB':int,
            'opMode':int,
            'navMode':int,
            'PDOP':float,
            'HDOP':float,
            'VDOP':float,
            'stdMajor':float,
            'stdMinor':float,
            'orient':float,
            'geometry':float,
            'dist':float}

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
                'dist']

types2 = {'timestamp':str,
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
            'numGP':int,
            'numGL':int,
            'numGA':int,
            'numGB':int,
            'opMode':str,
            'navMode':str,
            'PDOP':float,
            'HDOP':float,
            'VDOP':float,
            'stdMajor':float,
            'stdMinor':float,
            'orient':float,
            'geometry':float,
            'dist':float}

class NmeaDf:
    def __init__(self, filename):
        self.dateFormat = '%Y-%m-%dT%H:%M:%SZ'
        self.filename = filename

        global qualityFlag, navModeFlag, types1, header1
        self.qualityFlag = qualityFlag
        self.navModeFlag = navModeFlag
        self.types = types1
        self.header = header1


    def getDataFrame(self):

        df, valid = _import_df(self.filename,self.header,self.types,
                   self.dateFormat, self.navModeFlag)

        # Assing name to respective flag
        if 'navMode' in df.columns:
            df['navMode'] = df['navMode'].replace(navModeFlag)

        # Assing name to respective flag
        if 'navMode' in df.columns:
            df['navMode'] = df['navMode'].replace(navModeFlag)

        # Assing name to respective flag
        if 'posMode' in df.columns:
            posMode = _pos_dict()
            df['posMode'] = df['posMode'].replace(posMode['No Fix'], 'No Fix')
            df['posMode'] = df['posMode'].replace(posMode['Autonomous GNSS fix'], 'Autonomous GNSS fix')
            df['posMode'] = df['posMode'].replace(posMode['Differential GNSS fix'], 'Differential GNSS fix')
            df['posMode'] = df['posMode'].replace(posMode['RTK float'], 'RTK float')
            df['posMode'] = df['posMode'].replace(posMode['RTK fixed'], 'RTK fixed')

        # Remove pandas column Head

        return df, valid


class ResultDf:
    def __init__(self, filename, columns):
        self.dateFormat = '%Y-%m-%d %H:%M:%S'
        self.filename = filename
        global qualityFlag, navModeFlag, types2, header2
        self.qualityFlag = qualityFlag
        self.navModeFlag = navModeFlag
        self.types = types2
        self.header = header2
        self.columns = columns

    def get_df(self):

        df, valid = _import_df(self.filename,
                   self.header,
                   self.types,
                   self.dateFormat,
                   self.navModeFlag
                   )

        # Select only column accordint to columns list
        if valid:
            df = df[self.columns]

        # Assing name to respective flag
        if 'posMode' in df.columns:
            posMode = _pos_dict()
            df['posMode'] = df['posMode'].replace(posMode['No Fix'], 'No Fix')
            df['posMode'] = df['posMode'].replace(posMode['Autonomous GNSS fix'], 'Autonomous GNSS fix')
            df['posMode'] = df['posMode'].replace(posMode['Differential GNSS fix'], 'Differential GNSS fix')
            df['posMode'] = df['posMode'].replace(posMode['RTK float'], 'RTK float')
            df['posMode'] = df['posMode'].replace(posMode['RTK fixed'], 'RTK fixed')

        return df, valid

class StatDf:
    def __init__(self, filename, columns):
        self.dateFormat = '%Y-%m-%d %H:%M:%S'
        self.filename = filename

        global types2, header2, qualityFlag, navModeFlag
        self.qualityFlag = qualityFlag
        self.navModeFlag = navModeFlag
        self.types = types2
        self.header = columns

    def get_df(self):

        df, valid = _import_df(self.filename,
                   self.header,
                   self.types,
                   self.dateFormat,
                   self.navModeFlag
                   )



        return df, valid


