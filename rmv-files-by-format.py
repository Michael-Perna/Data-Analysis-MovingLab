# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 19:20:33 2021

@author: Michael
"""
import os
import glob

folder1 = 'C:\\SwisstopoMobility\\Analyse\\DataBase/**/*.results'
folder = 'D:\\2021/**/*.results'
folder2 = './DataBase/**/*results'

files = glob.glob(, recursive=True)

for f in files:
    try:
        os.remove(f)
    except OSError as e:
        print("Error: %s : %s" % (f, e.strerror))
