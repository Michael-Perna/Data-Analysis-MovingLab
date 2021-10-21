#!/usr/bin/env python
# coding: utf-8
"""Calculate GNSS errors precision respect to the railways reference."""


# Standard packages
import pandas as pd
import geopandas as gpd
from tqdm import tqdm

import warnings
import os

# Local Packages: Parser
from lib import nmea_df

# Local Packages: Tools
from lib import geolib as gl
from lib import gui_precision as gui
from lib import input_


# Ignore future warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class GetGnssError:
    """Estimate the receiver errors which is the ortho distance 2 the rail."""

    def __init__(self, filename: str):
        """Init."""
        self.filename = filename
        # Load rails als shapefile
        self.rail_back = gpd.read_file(input_.rail_back)
        self.rail_forth = gpd.read_file(input_.rail_forth)

    def main(self):
        """Do all neccessary step."""
        # ----------------------------------------------------------------
        # Import NMEA as dataframe
        # ----------------------------------------------------------------
        print('Data frame is uploading: ', self.filename)
        df_full, valid = nmea_df(self.filename)

        # ----------------------------------------------------------------
        # Change Projection
        # ----------------------------------------------------------------
        # Drop rows where there is no coordinates (No fix)
        df = df_full.dropna(subset=['lat', 'lon'])

        if 'sapcorda' in self.filename:
            df = gl.mn95_projection(df, degmin=True, itrf14=True)
        else:
            df = gl.mn95_projection(df, degmin=True)

        # Reinsert in df_full
        df_full.loc[df.index] = df

        # ----------------------------------------------------------------
        # Split Track
        # ----------------------------------------------------------------
        track_index = gl.split_track(df_full)

        # ----------------------------------------------------------------
        # Mesure distance to the reference rail
        # ----------------------------------------------------------------

        # Loop over each track
        loop = tqdm(total=100, position=0, desc='Calculating distances')
        for track in track_index:
            df = gl.dist2rail(df_full[track[0]:track[1]],
                              self.rail_back, self.rail_forth)
            gl.save_track(df, self.filename)
            loop.update(1)
        loop.close()

        # --------------------------------------------------------------
        # Save df_full as CSV
        # ----------------------------------------------------------------
        gl.save_all(df_full, self.filename)


class Batch:
    """Batch the GetGnssError() over all the .snmea files inside foldername."""

    def __init__(self, foldername):
        """Init."""
        self.foldername1 = foldername
        print('Start process\n\n')

    def scanDir(self):
        """Scan directory to search files with .snmea extension."""
        for entry in os.scandir(self.foldername1):
            if os.path.isdir(entry.path):
                self.foldername1 = entry
                self.scanDir()

            if os.path.isfile(entry.path):
                root, extension = os.path.splitext(entry.path)

                if extension == '.snmea':
                    print(f'File that is parsing {os.path.basename(entry)}: ')
                    tracks = GetGnssError(entry.path)
                    tracks.main()


app = gui.Interface()
app.title('Parse UBX messages')
app.mainloop()
filepath = app.output()
# filepath = 'C:/SwisstopoMobility/Analyse/DataBase/2021/05_May/18'

# Executre once for the selcted file
if os.path.isfile(filepath):
    tracks = GetGnssError(filepath)
    tracks.main()

# Iteration over all files in folder
if os.path.isdir(filepath):
    batch = Batch(filepath)
    batch.scanDir()
    print('End of batch process')
