
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 13:34:54 2020

@author: Michael
"""
import warnings
warnings.simplefilter(action='ignore')
from lib.import_df import ResultDf
import os
import errno
import lib.gui_concatTracks as gui
import geopandas as gpd
from geopandas.tools import sjoin


class Concat():
    def __init__(self, data_dir, receiver):
        self.zone_name = ''
        self.main_dir = './Analyse/DataBase'
        self.save_dir = './res/data/'
        self.loop_shp = '.\\maps\\railways\\loops.shp'
        self.zone = '.\\maps\\qgis-analysis\\areas-of-interest\\'+  self.zone_name[1:]+'.shp'

        self.receiver = receiver
        self.ext = '.results'
        self.data_dir = data_dir + self.ext
        self.foldername = data_dir
        self.outfile_name = self.save_dir + self.receiver+ self.zone_name + '.data'
        self.columns=['timestamp','lon','lat','posMode','numSV','difAge',
                       'HDOP','dist']

    # Taken from https://stackoverflow.com/a/600612/119527
    def mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

    def scanDir(self):

        for entry in os.scandir(self.foldername):
            if os.path.isdir(entry.path):
                self.foldername = entry
                self.scanDir()

            if os.path.isfile(entry.path):
                if os.stat(entry.path).st_size == 0: # remove empty file
                    os.remove(entry.path)
                    continue

                root, extension = os.path.splitext(entry.path)
                head, tail = os.path.split(root)
                if extension == self.ext and self.receiver in tail:
                    # Open outpufile in append mode
                    self.outfile = open(self.outfile_name, 'ab')

                    # Importation of tracks as Dataframe
                    timeseries = ResultDf(entry.path, self.columns)
                    df,valid = timeseries.get_df()
                    print(entry.path , valid)
                    # In case of the number of columns mismatch
                    if not valid:
                        continue

                    # ========= Zone analysis =========

                    # Remove NaN longitude and latitude for the gpd function
                    df2 = df[df['lon'].notna()] # df without NaN
                    df1 = df[df['lon'].isna()]  # df wih only Nan

                    # Transform lon, lan point to shapefile points
                    points = gpd.GeoDataFrame(df2,
                                     geometry=gpd.points_from_xy(df2.lon,
                                                                 df2.lat))
                    pointFrame = gpd.GeoDataFrame(
                                    geometry=gpd.GeoSeries(points.geometry))

                    # Upload unsafe area shapefile
                    poly = gpd.GeoDataFrame.from_file(self.zone)

                    # Join Both shapefile
                    pointInPolys = sjoin(pointFrame, poly, how='left')

                    # Remove index with duplicate values
                    if not pointInPolys.index.is_unique:
                        pointInPolys.index.duplicated()
                        pointInPolys = pointInPolys.loc[
                                        ~pointInPolys.index.duplicated(), :]

                    # Keep only point outside the join
                    df2 = df2[~pointInPolys.id.isnull()]

                    # Merge to the entire df to preserve epochs without position
                    df3 = df2.append(df1)

                    # ========= Remove those unsafe ans biased area for the analysis =========

                    ''' The tram when is in loops or bus station with multiple
                    tram platform it is not possible for the algorith to predict
                    in which rails the tram will be. Therefore I cannot apply
                    right reference and I remove those region. Morover the tram
                    continue to get GPS signals inside the depôt which is near the
                    railsway and it polluate the results. '''
                    # Remove NaN longitude and latitude for the gpd function
                    df2 = df3[df3['lon'].notna()] # df without NaN
                    df1 = df3[df3['lon'].isna()]  # df wih only Nan

                    # Transform lon, lan point to shapefile points
                    points = gpd.GeoDataFrame(df2,
                                     geometry=gpd.points_from_xy(df2.lon,
                                                                 df2.lat))
                    pointFrame = gpd.GeoDataFrame(
                                    geometry=gpd.GeoSeries(points.geometry))

                    # Upload unsafe area shapefile
                    poly = gpd.GeoDataFrame.from_file(self.loop_shp)

                    # Join Both shapefile
                    pointInPolys = sjoin(pointFrame, poly, how='left')

                    # Remove index with duplicate values
                    if not pointInPolys.index.is_unique:
                        pointInPolys.index.duplicated()
                        pointInPolys = pointInPolys.loc[
                                        ~pointInPolys.index.duplicated(), :]

                    # Keep only point outside the join
                    df2 = df2[pointInPolys.id.isnull()]

                    # Merge to the entire df to preserve epochs without position
                    df3 = df2.append(df1)

                    # Limit distance to mm to save memory space
                    df3['dist']=df3['dist'].round(3)

                    # Write only certain columns
                    df3.to_csv(self.outfile,
                            sep=',',
                            na_rep='',
                            columns=self.columns,
                            header=False,
                            index=False,
                            line_terminator = '\n')

                    self.outfile.close()



# Call the interface class
app = gui.Interface()
app.title('Concatenate file by day')
app.mainloop()
data_dir, receiver = app.output()

Concat(data_dir, receiver).scanDir()
