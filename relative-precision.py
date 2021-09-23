#!/usr/bin/env python
# coding: utf-8

# In[ ]:
# Module importation
from lib.import_df import NmeaDf
import numpy as np
from numpy.linalg import norm
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import geopandas as gpd
import math
import sys
sys.path.append('.\\lib\\geolib-master')
import swiss_projection
import os
import lib.gui_precision as gui
from tqdm import tqdm

# Shift CHTRF95 – ITRF2014 par mois
_drift = [['2020-12-31',0.492,-0.509,-0.382],
         ['2021-01-31',0.493,-0.511,-0.383],
         ['2021-02-28',0.495,-0.512,-0.384],
         ['2021-03-31',0.496,-0.514,-0.385],
         ['2021-04-30',0.497,-0.515,-0.386],
         ['2021-05-31',0.498,-0.517,-0.387],
         ['2021-06-30',0.499,-0.518,-0.388],
         ['2021-07-31',0.500,-0.520,-0.389],
         ['2021-08-31',0.501,-0.521,-0.390],
         ['2021-09-30',0.503,-0.523,-0.391],
         ['2021-10-31',0.504,-0.524,-0.392],
         ['2021-11-30',0.505,-0.526,-0.393],
         ['2021-12-31',0.506,-0.527,-0.394]]

# Not efficient Added in september
_drift = pd.DataFrame(_drift, columns = ['epoch', 'dx', 'dy', 'dz'])
_drift.epoch = pd.to_datetime(_drift.epoch, format='%Y-%m-%d')
_drift['t'] = _drift.epoch - _drift.epoch[0]
_tp = _drift.t.dt.days.astype(int).to_numpy()

# In[62]:
# Class Containtg main func tion
class SplitTrack:

    def __init__(self, filename):
        # dataframe with the coordinates
        self.filename = filename
        self.start = False
        self.stop = False

        # Get rails shapefile
        self.rail_back = '.\\maps\\railways\\backward_track_Adjusted.shp'
        self.rail_forth ='.\\maps\\railways\\foward_track_Adjusted.shp'
        # Get distance form rail and save each tracks
        root, tail = os.path.split(self.filename)
        self.head, self.ext = os.path.splitext(tail)
        self.folder_name = root + '/tracks/'
        global _tp, _drift
        self.tp = _tp
        self.drift = _drift
        self.fx = _drift.dx.to_numpy()
        self.fy = _drift.dy.to_numpy()
        self.fz = _drift.dz.to_numpy()

    def degmin2deg(self, degmin):
        # Transformation en degrées depuis degàes minutes
        a, b = str(degmin).split('.')
        d = int(a[:-2])
        m = float(a[-2:] + '.'+ b)

        degrees = d + m/60
        #rad = degrees*180/np.pi
        return degrees

    def is_inbox(self, x,y,box):
        # Cette function test si les point ce trouve dans un carré
        if x > box[0,0] and x < box[1,0]:
            if y > box[0,1] and y < box[1,1]:
                return True
        else:
            return False

    def is_inloop(self, x,y):
        # Le tram aux termiuns fait des loop est change de sens est de "railles"
        # ainsi la référence aussi. Si le tram ce trouve dans une de ces quatre
        # loop la function röpond True
        box1 = np.matrix('2498300, 1114715; 2498361, 1114780')
        box2 = np.matrix('2498762, 1114269; 2498820, 1114307')
        box3 = np.matrix('2499583, 1114983; 2499652, 1115047')
        box4 = np.matrix('2504780, 1116346; 2504949, 1116475')
        # box5 =  np.matrix('2498977, 1114431; 2499183, 1114749')

        return self.is_inbox(x,y,box1) or self.is_inbox(x,y,box2) \
                or self.is_inbox(x,y,box3) or self.is_inbox(x,y,box4)
                # or self.is_inbox(x,y,box5)

    def angle_Eaxis_dist(self, pproj, point):
        n1 = np.array([1, 0])
        x2 = point.coords[0][0] - pproj.coords[0][0]
        y2 = point.coords[0][1] - pproj.coords[0][1]
        d =  np.array([x2, y2])
        n2 = d / norm(d)

        angle = np.arctan(np.dot(n1,n2)/(norm(n1)*norm(n2)))

        return np.degrees(angle)

    def projectionOnLateralTramAxe(self, stdMajor, stdMinor, orient, point, pproj):
        angle_Eaxis = self.angle_Eaxis_dist(pproj, point)

        '''get the orientation of the major axis on the"local Tram" Frame :
            the orientation of the semi-major axis of error ellipse
            is given in degrees from true north and has values in the range
            [0,180] '''

        new_orient = orient + angle_Eaxis - 90
        stdMajorTramAxe = abs(stdMajor*np.cos(np.radians(new_orient)))
        stdMinorTramAxe = abs(stdMinor*np.sin(np.radians(new_orient)))

        return stdMajorTramAxe, stdMinorTramAxe

    def errors(self, stdMajor, stdMinor, orient, point, polyline, df):
        # Distance minimal entre le point et la linge par itératio
        # C'est pas gönial car je teste toute les distances possible

        ''' Distance "d" of the point from the polyline (rails) and get also the
        point projection "pp" on the polyline '''
        dist = 90000
        for line in polyline['geometry']:
            d_new = line.distance(point)
            pp_new = line.project(point)
            if d_new < dist:
                dist = d_new
                pp = pp_new
        pp = line.interpolate(pp)


        ''' Projection of the standard deviation of the major and minor axis
        of the GNSS point onto the axis with same norm has dist (calcued has
        dist = point - pp)'''
        Sax, Sbx = self.projectionOnLateralTramAxe(stdMajor, stdMinor, orient,
                                                 point, pp)

        ''' Change scale from meter to centimeters and round to mm'''
        dist = round(dist*100, 1)
        Sax = (Sax*100).round(decimals=1)
        Sbx = (Sbx*100).round(decimals=1)

        ''' Standirize the error ("dist") by the standart deviation on the same
        orientation of dist given computed from the receiver std major and
        minor axis (Qxx)'''
        Sy_tram = np.sqrt(Sax**2 + Sbx**2)
        Sy_tram = Sy_tram.round(1)    # round to mm

        ''' This if is made to avoid uncontroled  change in the err unit if
        Sy_tram is under 1 cm '''
        if Sy_tram >= 1:
            err = dist / Sy_tram
            # Round err to mm (is already expressed in cm)
            err = round(err, 1)
        elif Sy_tram<1 :
            # si plus petit que l'ordre du centimütre
            err = (dist / Sy_tram)/10
            # Round err to mm (is already expressed in cm)
            err = round(err, 1)
        elif np.isnan(Sy_tram):
            err = None
        elif np.isnan(dist):
            err = None
        else:
            print('Houston err in errors() has a problem', Sy_tram)



        # Get the great value between Sax and Sbx to used in an integrity test
        Smax = max(Sax, Sbx)

        return dist, err, pp, Sy_tram, Smax

    def classify_track(self, df):
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

            # ========= Change Projection =========
        if 'sapcorda' in self.filename:
            # Converstion from itrf14 to lv95
            # Progress bar
            loop = tqdm(total = len(alt) ,
                        desc='Coordinates transformation ..',
                        position =0, leave=False)

    def projection(self, df,  df_full, lon, lat, alt):
        if 'sapcorda' in self.filename:
            # Converstion from itrf14 to lv95
            # Progress bar
            loop = tqdm(total = len(alt),
                        desc='Coordinates transformation ..',
                        position =0, leave=False)

            for i in range(len(alt)):
                # llh vector
                llh1 = [lon[i].tolist()[0],
                        lat[i].tolist()[0],
                        alt[i].tolist()[0]]

                ''' Apply linear interpolation between two months calculated
                drift to get an drift values for the day. The drift is needed
                to change the coor. ref. system from ITRF2014 at the current
                epoch to the CHRF95 '''

                # Create a time series "t" with as number of days delaied from
                # first epoch corretin : t = timestamp_now - epoch[0]
                t = df_full.loc[df['index'][i],['timestamp']
                                ][0] - self.drift.epoch[0]

                t = t.days  # convert time delay in number od days

                # applay numpy interpolation functio
                dx = np.interp(t, self.tp, self.fx)
                dy = np.interp(t, self.tp, self.fy)
                dz = np.interp(t, self.tp, self.fz)

                # Apply the projection on coord
                df_full.loc[df['index'][i],['lon','lat','alt']] \
                    = swiss_projection.wgs84_itrf14_to_lv95(llh1, [dx,dy,dz])

                # Progress bar: loop.set_description('i = %d', i )
                loop.update(1)
            loop.close()
            return df_full

        else:
            # Converstion to lv95
            # Progress bar
            # print('Starting cooridnates transformation loop .. ')
            loop = tqdm(total = len(alt),
                        desc='Coordinates transformation ..', position =0)

            for i in range(len(alt)):
                # llh vector
                llh1 = [lon[i].tolist()[0],
                        lat[i].tolist()[0],
                        alt[i].tolist()[0]]


                 # Apply the projection on coord llh1
                df_full.loc[df['index'][i],['lon','lat','alt']] \
                    = swiss_projection.wgs84_to_lv95(llh1)

                # Progress bar:
                loop.update(1)
            loop.close()
        return df_full

    def split_track(self,df_full, lon, lat):
        # Progress bar
        loop = tqdm(total = len(lon)-4 , position =0,
                        desc="Dividing full track ..")

        # Loop initialization
        track_index = np.zeros((100,2)).astype(int)     # 100 i a guess
        n = 0

        for i in range(len(lon)-4):
            # This method cann be applied as the tram follow a growing
            # longitude path (or viceversa decreasing)
            # track index is matrix with:
            #
            #  num°Track: index_start, index_end
            #      0         52            11120

            # START (quitting the loop)
            if self.is_inloop(lon[i], lat[i]) \
                and not self.is_inloop(lon[i+1], lat[i+1]):
                track_index[n,0] = i
                self.start = True
                self.stop = False

            # STOP (entering the loop)
            if not self.is_inloop(lon[i], lat[i]) \
                and self.is_inloop(lon[i+1], lat[i+1]):
                # STOP
                track_index[n,1] = i
                n += 1
                self.stop = True
                self.start = False

            delta = df_full['timestamp'].iloc[i+1]-df_full['timestamp'].iloc[i]

            # If the there is a time gap great than five minutes break
            # Why ?
            if delta.total_seconds()>300 and self.start == True:
                track_index[n,1] = i
                n += 1

                # Start
                track_index[n,0] = i +1

            # Progress bar:
            loop.update(1)
        loop.close()
        return track_index

    def get_distance_and_save(self, track_index, df_full, loop):

        # Load rails als shapefile
        rail_back = gpd.read_file(self.rail_forth)
        rail_forth = gpd.read_file(self.rail_back)

        # if the directory does not exist it create it
        folder_name = self.head  +  '/tracks'
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)
            print("created folder : ", folder_name)

        for i in range(60): # I cannot say forehad how many track there woud be
            if track_index[i,0] !=0:

                df2 = df_full[track_index[i,0]: track_index[i,1]]
                df2 = df2.reset_index(drop=True)

                # skip csv with less than one epoch
                if df2.empty or len(df2)<=1:
                    continue

                # Distinguish back and forth tram travel
                track_type = self.classify_track(df2)

                # Lon/Lat to gpd points geometry
                gpd.GeoDataFrame(df2,
                                 geometry=gpd.points_from_xy(df2.lon, df2.lat))

                # Initialize loop variable
                dist = [None]*len(df2['geometry'])
                pproj = [None]*len(df2['geometry'])
                err = [None]*len(df2['geometry'])
                Sytram = [None]*len(df2['geometry'])
                Smax = [None]*len(df2['geometry'])

                ''' Get information about the GNSS mesure errors
                        "dist" :  orthogonal distance between point and rail
                                  which is the absolute errors of the GNSS
                                  point

                        "pproj":  projection of the GNSS point onto the rail
                                  line

                        "err":    standarized absolute errors.
                                  err = dist /sqrt(Sax^2+Sbx^2)

                                  where Sax is the standard deviation of the
                                  major axis projected onto the an axis with
                                  share the same norm as "dist". Sbx is the
                                  respective projected standard deviation of
                                  the minor axis

                        "Sytram":   Is the greater values between Sax and Sbx '''

                if track_type == 'foward':
                    for index, row in df2.iterrows():
                        if not math.isnan(row['geometry'].x) \
                            or not math.isnan(row['geometry'].x):
                            dist[index], err[index], pproj[index], \
                            Sytram[index], Smax[index] \
                                = self.errors(row['stdMajor'],
                                              row['stdMinor'], row['orient'],
                                              row['geometry'], rail_forth, df2)
                    df2['dist'] = dist
                    df2['pproj'] = pproj
                    df2['err'] = err
                    df2['Sytram'] = Sytram
                    df2['Smax'] = Smax

                elif track_type == 'backward':
                    for index, row in df2.iterrows():
                        if not math.isnan(row['geometry'].x) \
                            or not math.isnan(row['geometry'].x):
                            dist[index], err[index],pproj[index], \
                            Sytram[index], Smax[index] = \
                                self.errors(row['stdMajor'],
                                            row['stdMinor'],row['orient'],
                                            row['geometry'], rail_back, df2)
                    df2['dist'] = dist
                    df2['pproj'] = pproj
                    df2['err'] = err
                    df2['Sytram'] = Sytram
                    df2['Smax'] = Smax

                elif track_type == 'too small':
                    continue
                else:
                    print('there is a problem')

                # ==================== Save the Results ======================
                start = df_full['timestamp'].iloc[track_index[i,0]].strftime('%H_%M_%S')
                end =  df_full['timestamp'].iloc[track_index[i,1]].strftime('%H_%M_%S')

                # if the directory does not exist it create it
                if not os.path.isdir(self.folder_name):
                    os.makedirs(self.folder_name)
                    print("Created folder : ", self.folder_name)

                file_name = self.folder_name + self.head +'__' + start + '_'+ end \
                            + ".results"

                df2.to_csv(file_name,
                            sep=',',
                            na_rep='',
                            header=False,
                            index=False,
                            line_terminator = '\n')

            loop.update(1)
        loop.close()


    def main(self):

        # Importation of NMEA as Dataframe
        timeseries = NmeaDf(self.filename)
        print('Data frame is uploading: ', self.filename)
        df_full, valid = timeseries.getDataFrame()


        # ========================= Change Projection =========================
        # Drop rows where there is no coordinates (No fix)
        df = df_full.dropna(subset=['lat', 'lon']).reset_index(drop=False)

        # Convert in degree (nmea format)
        df.loc[:,'lon'] = df.loc[:,'lon'].apply(self.degmin2deg)
        df.loc[:,'lat'] = df.loc[:,'lat'].apply(self.degmin2deg)

        # Dataframe to matrix
        lon =  pd.DataFrame(df['lon']).to_numpy()
        lat =  pd.DataFrame(df['lat']).to_numpy()
        alt =  pd.DataFrame(df['alt']).to_numpy()

        df_full = self.projection(df, df_full, lon, lat, alt)

         # ========================= Split Track ===============================
        # Dataframe to matrix
        df_full['timestamp'] = pd.to_datetime(df_full['timestamp'],
                                              format='%Y-%m-%dT%H:%M:%SZ')

        lon =  pd.DataFrame(df_full['lon']).to_numpy()
        lat =  pd.DataFrame(df_full['lat']).to_numpy()

        track_index = self.split_track(df_full, lon,lat)

        # ===================== Mesure distance to Rail =======================
        # Progress bar
        loop = tqdm(total = 100 , position =0, desc='Calculating distances')

        # Remove empty line from track_index
        mask = np.any(np.isnan(track_index), axis=1)
        track_index = track_index[~mask]
        track_index = track_index.astype(int)

        self.get_distance_and_save(track_index,df_full,loop)


        # ========= Save as CSV =========
        # save the entire dataframe as a csv file
        # skip csv with less than one epoch
        if df_full.empty or len(df_full)<=1:
            return
        # save the entire dataframe as a csv file
        folder_name = self.folder_name + 'csv/'
        # if the directory does not exist it create it
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)


        df_full.to_csv(folder_name + self.head+ ".csv", index=False)



class Batch:
    def __init__(self, foldername):
        self.foldername1 = foldername
        # self.count = 1
        # self.numFiles = self.countFiles(foldername)

        print('Start process\n\n')

    def scanDir(self):

        for entry in os.scandir(self.foldername1):
            if os.path.isdir(entry.path):
                self.foldername1 = entry
                self.scanDir()

            if os.path.isfile(entry.path):
                root, extension = os.path.splitext(entry.path)

                if extension == '.snmea':
                    print(f'File that is parsing {os.path.basename(entry)}: ')
                    tracks = SplitTrack(entry.path)
                    tracks.main()


# In[]:
# Call the interface class
# app = gui.Interface()
# app.title('Parse UBX messages')
# app.mainloop()
# filepath = app.output()
filepath = 'C:/SwisstopoMobility/Analyse/DataBase/2021/05_May/18'

# Executre once for the selcted file
if os.path.isfile(filepath):
    tracks = SplitTrack(filepath)
    tracks.main()

# Iteration over all files in folder
if os.path.isdir(filepath):
    batch = Batch(filepath)
    batch.scanDir()
    print('End of batch process')
