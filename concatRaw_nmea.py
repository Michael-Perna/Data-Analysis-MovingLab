
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 13:34:54 2020

@author: Michael
"""
import shutil
import glob
import os
from datetime import datetime
import errno
import lib.gui_concat as gui

class Concat():
    def __init__(self, data_dir, output, ext ):
        # self.main_dir ='C:/SwisstopoMobility/analysis/DataBase'
        # self.output = 'sapcorda_ubx.ubx'
        # self.data_dir = 'C:/SwisstopoMobility/analysis/data/Wabern_Rooftop_20122020/sapcorda_ubx/*.ubx'
        self.main_dir = 'C:/SwisstopoMobility/Analyse/DataBase'
        self.output = output + ext
        self.data_dir = data_dir + '/*' + ext
        self.date_old = datetime(1,1,1)
        self.is_open = False
        print(self.output)
        print(self.data_dir)
        
    # Taken from https://stackoverflow.com/a/600612/119527
    def mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise
    
    # Taken from https://stackoverflow.com/a/600612/119527
    def safe_open_wb(self, file_name):
        ''' Open "path" for writing, creating any parent directories as needed.
        '''
        
        self.mkdir_p(os.path.dirname(file_name))
        outfile_name = self.uniquefilename(file_name)
        print(outfile_name)
        return open(outfile_name, 'wb')
    
    def uniquefilename(self, path_name):
        print(os.path.isfile(path_name))
        if os.path.isfile(path_name):
            info = os.path.splitext(path_name)
            print(info)
            path_name = info[0] + '-copy' + info[1]
            print(path_name)
            path_name = self.uniquefilename(path_name)
            
        return path_name
    
    def isnewday(self, date_old, date_new):
        
        if date_new.day == date_old.day:
            return False
        else:
            return True
        
    def makepath(self,date):
        year = date.year
        month = date.strftime('%B')
        month2 =date.month
        day = date.day
        
        outfile_name = self.main_dir + '/' \
                + str(year) + '/' \
                + str(month) + '/' \
                + str(day).zfill(2) + '/' \
                + str(year)+'-'+ str(month2).zfill(2) +'-'+ str(day).zfill(2) + '_'+ self.output
                
                        
        return outfile_name
   
    def concat(self):

        # Change main directory
        for filename in glob.glob(self.data_dir):
            if filename == self.output:
                # don't want to copy the output into the output
                continue
            basename = os.path.basename(filename)

            try:
                date = basename[0:10]
                date_new = datetime.strptime(date, '%Y-%m-%d')

            except Exception as e:
                # print(e)
                pass
            try:
                date = basename[0:10]
                date_new = datetime.strptime(date, '%d-%m-%Y')

                
            except Exception as e:
                # print(e)
                # print(date, ':()')
                pass

            # If new day concatante in new place 
            # print(date, type(date), str(dat()))
            # print(date, type(self.date_old))

            if self.isnewday(date_new, self.date_old):
                # Close previous file
                if self.is_open:
                     self.outfile.close()
                     self.is_open = False
                # Create path for the new output
                outfile_name = self.makepath(date_new)
                # Open outpufile
                self.outfile = self.safe_open_wb(outfile_name)
                self.is_open = True
                # Update day
                self.date_old = date_new
                
            with open(filename, 'rb') as readfile:
                print(filename, ' :)')
                # print(outfile_name)
                shutil.copyfileobj(readfile, self.outfile)
                readfile.close()
                os.remove(filename)

class Rmvemptyfld():
   
    def __init__(self, maind_dir):
        self.main_dir = main_dir
        

    def scanDir(self):
        for entry in os.scandir(self.main_dir):
            if os.path.isdir(entry.path) and not os.listdir(entry.path) :
                os.rmdir(entry.path)
                print(f'Folder {entry} removed')
            elif os.path.isdir(entry.path):
                self.main_dir = entry
                self.scanDir()
                
    
# Call the interface class
app = gui.Interface()
app.title('Concatenate file by day')
app.mainloop()
main_dir, output, ext = app.output()

Concat(main_dir, output, ext).concat()
main_dir = 'C:\\SwisstopoMobility\\Analyse\\data'
Rmvemptyfld(main_dir).scanDir()