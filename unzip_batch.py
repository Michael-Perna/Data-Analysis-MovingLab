# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 09:07:46 2021

@author: Michael
"""
import os, zipfile

dir_name = 'C:\\SwisstopoMobility\\analysis\\DataBase\\2021\\February\\10\\rinex'
dir_name = os.path.abspath(dir_name)
extension = ".zip"

os.chdir(dir_name) # change directory from working dir to dir with files

for item in os.listdir(dir_name): # loop through items in dir
    if item.endswith(extension): # check for ".zip" extension
        file_name = os.path.abspath(item) # get full path of files
        zip_ref = zipfile.ZipFile(file_name) # create zipfile object
        zip_ref.extractall(dir_name) # extract file to dir
        zip_ref.close() # close file
        os.remove(file_name) # delete zipped filef