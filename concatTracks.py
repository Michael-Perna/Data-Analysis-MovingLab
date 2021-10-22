# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 13:34:54 2020.

@author: Michael
"""

# Import standard modules$
import errno
import os

# Import local modules
from lib import gui_concatTracks as gui
from lib import geolib as gl
from lib import result_df
from lib import input_

_columns = ['timestamp', 'lon', 'lat', 'posMode', 'numSV', 'difAge',
            'HDOP', 'dist']


class Concat():
    """Concat all track wanted for the analysis."""

    def __init__(self, folder_name: str, receiver_name: str, zone: str,
                 save_csv: bool, columns=_columns):
        """Init."""
        self.foldername = folder_name
        self.receiver_name = receiver_name
        self.zone_file = zone
        self.save_csv = save_csv
        self.columns = columns

        self.files = []
        self.outfile_name = input_.results + receiver_name +\
            '_' + input_.zone_dict[zone] + '.csv'

        if not os.path.isdir(input_.results):
            os.makedirs(input_.results)
            print("created folder : ", input_.results)

    def scanDir(self):
        # FIXME: not right way to do function input output
        """Scan self.folder name directory and return a list."""
        for entry in os.scandir(self.foldername):
            if os.path.isdir(entry.path):
                self.foldername = entry
                self.scanDir()

            if os.path.isfile(entry.path):
                if os.stat(entry.path).st_size == 0:  # remove empty file
                    os.remove(entry.path)
                    continue

                root, extension = os.path.splitext(entry.path)
                head, tail = os.path.split(root)

                if extension == '.results' and self.receiver_name in tail:
                    self.files.append(entry.path)

    def main(self):

        self.scanDir()
        for file in self.files:
            if self.save_csv:

                # Open outpufile in append mode
                self.outfile = open(self.outfile_name, 'ab')

            # Importation of tracks as Dataframe
            df, valid = result_df(file, self.columns)
            print(file, valid)

            # In case of the number of columns mismatch
            if not valid:
                continue

            df = gl.select_zone(df, self.zone_file)

            if self.save_csv:
                # Write only certain columns
                df.to_csv(self.outfile, sep=',', na_rep='',
                          columns=self.columns, header=False, index=False,
                          line_terminator='\n')
            return df


folder_name = './DataBase'
receiver_name = 'sapcorda'
zone = input_.city_NS
df = Concat(folder_name, receiver_name, zone, save_csv=True).main()
