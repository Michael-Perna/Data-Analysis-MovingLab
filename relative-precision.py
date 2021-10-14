#!/usr/bin/env python
# coding: utf-8
"""Calculate GNSS errors precision respect to the railways reference."""
# In[ ]:
# Module importation
import lib.swiss_projection
from lib.load_df import NmeaDf
import numpy as np
import warnings
import pandas as pd
import geopandas as gpd
import math
import sys
import os
import lib.gui_precision as gui
from tqdm import tqdm
sys.path.append('.\\lib\\geolib-master')
warnings.simplefilter(action='ignore', category=FutureWarning)


# Shift CHTRF95 – ITRF2014 for each month in the year 2021
drift = [['2020-12-31', 0.492, -0.509, -0.382],
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

# Not efficient Added in september
drift = pd.DataFrame(drift, columns=['epoch', 'dx', 'dy', 'dz'])
drift.epoch = pd.to_datetime(drift.epoch, format='%Y-%m-%d')
drift.t = drift.epoch - drift.epoch[0]
tp = drift.t.dt.days.astype(int).to_numpy()

# In[62]:
# Class Containtg main func tion


class GetError:
    """Estimate the receiver errors which is the ortho distance 2 the rail."""

    def __init__(self, filename: str):
        # dataframe with the coordinates
        self.filename = filename
        self.start = False
        self.stop = False

        # Get rails shapefile
        self.rail_back = '.\\maps\\railways\\backward_track_Adjusted.shp'
        self.rail_forth = '.\\maps\\railways\\foward_track_Adjusted.shp'

        # Get distance form rail and save each tracks
        root, tail = os.path.split(self.filename)
        self.head, self.ext = os.path.splitext(tail)
        self.folder_name = root + '/tracks/'
        global tp, drift
        self.tp = tp
        self.drift = drift

    def degmin2deg(self, degmin: str):
        """Transform string containig degree minutes data into float degree."""
        a, b = str(degmin).split('.')
        d = int(a[:-2])
        m = float(a[-2:] + '.' + b)

        degrees = d + m/60
        return degrees

    def is_inbox(self, x: float, y: float, box: list):
        """Answer True if the point (x,y) is inside the 'box'."""
        if x > box[0, 0] and x < box[1, 0]:
            if y > box[0, 1] and y < box[1, 1]:
                return True
        else:
            return False

    def is_inloop(self, x: float, y: float):
        """
        Check if the point is inside a rail loop.

        Parameters
        ----------
        x : float
            Longitute in MN95 reference frame.
        y : float
            Latitude in MN95 reference frame.

        Returns
        -------
        Boolean
            True if the point (x,y) is inside a Terminal loop of the tram 12 of
            the TPG (Transport Public Genevois).

        """
        box1 = np.matrix('2498300, 1114715; 2498361, 1114780')
        box2 = np.matrix('2498762, 1114269; 2498820, 1114307')
        box3 = np.matrix('2499583, 1114983; 2499652, 1115047')
        box4 = np.matrix('2504780, 1116346; 2504949, 1116475')
        # box5 =  np.matrix('2498977, 1114431; 2499183, 1114749')

        return self.is_inbox(x, y, box1) or self.is_inbox(x, y, box2) \
            or self.is_inbox(x, y, box3) or self.is_inbox(x, y, box4)
        # or self.is_inbox(x,y,box5)

    def distance_pt2shpline(self, point, polyline):
        """Calulate the shorter distance between 'point' and 'polyline'."""
        d = 90000
        for line in polyline['geometry']:
            d_new = line.distance(point)
            if d_new < d:
                d = d_new
        return d

    def classify_track(self, df):
        """
        Assign an orientation to each track.

        Parameters
        ----------
        df : dataframe
            dataframe containing track data.

        Returns
        -------
        track: str
            'backward': the tram is moving from the station Moisullaz to Bachet
            'foward':   the tram is moving from the station Bachet to Moisullaz

        """
        # remove nan position
        small_df = df.dropna(subset=['lat', 'lon']).reset_index(drop=False)

        if small_df.empty or len(small_df) <= 1:
            return 'too small'
        # look at first longitude
        first = small_df['lon'].iloc[1]
        # look at last longitude
        last = small_df['lon'].iloc[-1]

        # Define the track orientation
        if first > last:
            track = 'backward'
        elif first < last:
            track = 'foward'
        else:
            print('Huston we have a problem!')
            return 'problem'
        return track

    def projection(self, df, df_full, lon, lat, alt):
        """
        Project lon, lat, alt coord. from CHTRF95 or in ITRF14 into MN95.

        Parameters
        ----------
        df : dataframe
            dataframe containing data of one single track.
        df_full : dataframe
            dataframe containing data all the tracks.
        lon : list
            Longitude either in CHTRF95 or in ITRF14.
        lat : list
            Longitude either in CHTRF95 or in ITRF14.
        alt : list
            Altitude either in CHTRF95 or in ITRF14.

        Returns
        -------
        df_full : TYPE
            DESCRIPTION.

        """
        if 'sapcorda' in self.filename:
            # Converstion from itrf14 to lv95
            # Progress bar
            loop = tqdm(total=len(alt),
                        desc='Coordinates transformation ..',
                        position=0, leave=False)

            for i in range(len(alt)):
                # llh vector
                llh = [lon[i].tolist()[0],
                       lat[i].tolist()[0],
                       alt[i].tolist()[0]]

                t = df_full.loc[df['index'][i], [
                    'timestamp']][0] - self.drift.epoch[0]

                fx = self.drift.dx.to_numpy()
                fy = self.drift.dy.to_numpy()
                fz = self.drift.dz.to_numpy()
                t = t.days
                dx = np.interp(t, self.tp, fx)
                dy = np.interp(t, self.tp, fy)
                dz = np.interp(t, self.tp, fz)

                df_full.loc[df['index'][i], ['lon', 'lat', 'alt']] \
                    = swiss_projection.wgs84_itrf14_to_lv95(llh, [dx, dy, dz])

                # Progress bar: loop.set_description('i = %d', i )
                loop.update(1)
            loop.close()
            return df_full

        else:
            # Converstion to lv95
            # Progress bar
            # print('Starting cooridnates transformation loop .. ')
            loop = tqdm(total=len(alt),
                        desc='Coordinates transformation ..', position=0)

            for i in range(len(alt)):
                # llh vector
                llh = [lon[i].tolist()[0],
                       lat[i].tolist()[0],
                       alt[i].tolist()[0]]

                # conversion
                df_full.loc[df['index'][i], ['lon', 'lat', 'alt']] \
                    = swiss_projection.wgs84_to_lv95(llh)

                # Progress bar:
                loop.update(1)
            loop.close()
        return df_full

    def split_track(self, df_full, lon: list, lat: list):
        """Split the data series in track data that are on the same rail.

        Description
        -----------
            This method cann be applied as the tram follow a growing longitude
            path (or viceversa decreasing).

            The 'track_index':  is a matrix with:

                num°Track: index_start, index_end
                ---------------------------------
                  0         52            11120
        """
        # Progress bar
        loop = tqdm(total=len(lon)-4, position=0,
                    desc="Dividing full track ..")

        # Loop initialization
        track_index = np.zeros((100, 2)).astype(int)     # 100 i a guess
        n = 0

        for i in range(len(lon)-4):
            # START (quitting the loop)
            if self.is_inloop(lon[i], lat[i]) \
                    and not self.is_inloop(lon[i+1], lat[i+1]):
                track_index[n, 0] = i
                self.start = True
                self.stop = False

            # STOP (entering the loop)
            if not self.is_inloop(lon[i], lat[i]) \
                    and self.is_inloop(lon[i+1], lat[i+1]):
                # STOP
                track_index[n, 1] = i
                n += 1
                self.stop = True
                self.start = False

            delta = df_full['timestamp'].iloc[i+1]-df_full['timestamp'].iloc[i]

            # If the there is a time gap great than five minutes break
            if delta.total_seconds() > 300 and self.start is True:
                track_index[n, 1] = i
                n += 1

                # Start
                track_index[n, 0] = i + 1

            # Progress bar:
            loop.update(1)
        loop.close()
        return track_index

    def get_distance_and_save(self, track_index, df_full, loop):
        """Loop over each track calculate the GNSS error and save the track."""
        # Load rails als shapefile
        rail_back = gpd.read_file(self.rail_forth)
        rail_forth = gpd.read_file(self.rail_back)
        # if the directory does not exist it create it
        folder_name = self.head + '/tracks'
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)
            print("created folder : ", folder_name)

        # I cannot say forehad how many track there woud be
        for i in range(60):
            if track_index[i, 0] != 0:

                df2 = df_full[track_index[i, 0]: track_index[i, 1]]
                df2 = df2.reset_index(drop=True)

                # skip csv with less than one epoch
                if df2.empty or len(df2) <= 1:
                    continue

                # Distinguish back and forth tram travel
                track_type = self.classify_track(df2)

                # Lon/Lat to gpd points geometry
                gpd.GeoDataFrame(df2,
                                 geometry=gpd.points_from_xy(df2.lon, df2.lat))

                # Mesure distance from the rail
                dist = [None]*len(df2['geometry'])
                if track_type == 'foward':
                    for index, row in df2.iterrows():
                        if not math.isnan(row['geometry'].x) \
                                or not math.isnan(row['geometry'].x):
                            dist[index] = self.distance_pt2shpline(
                                row['geometry'], rail_forth)
                    df2['dist'] = dist
                elif track_type == 'backward':
                    for index, row in df2.iterrows():
                        if not math.isnan(row['geometry'].x) \
                                or not math.isnan(row['geometry'].x):
                            dist[index] = self.distance_pt2shpline(
                                row['geometry'], rail_back)
                    df2['dist'] = dist
                elif track_type == 'too small':
                    continue
                else:
                    print('there is a problem')

                # ==================== Save the Results ======================
                start = df_full['timestamp'].iloc[track_index[i, 0]].strftime(
                    '%H_%M_%S')
                end = df_full['timestamp'].iloc[track_index[i, 1]
                                                ].strftime('%H_%M_%S')

                # if the directory does not exist it create it
                if not os.path.isdir(self.folder_name):
                    os.makedirs(self.folder_name)
                    print("Created folder : ", self.folder_name)

                file_name = self.folder_name + self.head + '__' + start + \
                    '_' + end + ".results"

                df2.to_csv(file_name,
                           sep=',',
                           na_rep='',
                           header=False,
                           index=False,
                           line_terminator='\n')

            loop.update(1)
        loop.close()

    def main(self):
        """Do all neccessary step."""
        # Importation of NMEA as Dataframe
        timeseries = NmeaDf(self.filename)
        print('Data frame is uploading: ', self.filename)
        df_full, valid = timeseries.getDataFrame()

        # ========================= Change Projection =========================
        # Drop rows where there is no coordinates (No fix)
        # df_b= df.dropna(subset=['lat', 'lon']).reset_index(drop=True)
        df = df_full.dropna(subset=['lat', 'lon']).reset_index(drop=False)

        # Convert in degree (nmea format)
        df.loc[:, 'lon'] = df.loc[:, 'lon'].apply(self.degmin2deg)
        df.loc[:, 'lat'] = df.loc[:, 'lat'].apply(self.degmin2deg)

        # Dataframe to matrix
        lon = pd.DataFrame(df['lon']).to_numpy()
        lat = pd.DataFrame(df['lat']).to_numpy()
        alt = pd.DataFrame(df['alt']).to_numpy()

        df_full = self.projection(df, df_full, lon, lat, alt)

        # ========================= Split Track ===============================
        # Dataframe to matrix
        df_full['timestamp'] = pd.to_datetime(df_full['timestamp'],
                                              format='%Y-%m-%dT%H:%M:%SZ')

        lon = pd.DataFrame(df_full['lon']).to_numpy()
        lat = pd.DataFrame(df_full['lat']).to_numpy()

        track_index = self.split_track(df_full, lon, lat)

        # ===================== Mesure distance to Rail =======================
        # Progress bar
        loop = tqdm(total=100, position=0, desc='Calculating distances')

        # Remove empty line from track_index
        mask = np.any(np.isnan(track_index), axis=1)
        track_index = track_index[~mask]
        track_index = track_index.astype(int)

        self.get_distance_and_save(track_index, df_full, loop)

        # ========= Save as CSV =========
        # save the entire dataframe as a csv file
        # skip csv with less than one epoch
        if df_full.empty or len(df_full) <= 1:
            return
        # save the entire dataframe as a csv file
        self.folder_name = self.folder_name + 'csv/'
        # if the directory does not exist it create it
        if not os.path.isdir(self.folder_name):
            os.makedirs(self.folder_name)

        df_full.to_csv(self.folder_name + self.head + ".csv", index=False)


class Batch:
    """Batch the GetError() over all the .snmea files inside foldername."""

    def __init__(self, foldername):
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
                    tracks = GetError(entry.path)
                    tracks.main()


# In[]:
# Call the interface class
app = gui.Interface()
app.title('Parse UBX messages')
app.mainloop()
filepath = app.output()
# filepath = 'C:/SwisstopoMobility/Analyse/DataBase/2021/05_May/18'

# Executre once for the selcted file
if os.path.isfile(filepath):
    tracks = GetError(filepath)
    tracks.main()

# Iteration over all files in folder
if os.path.isdir(filepath):
    batch = Batch(filepath)
    batch.scanDir()
    print('End of batch process')
