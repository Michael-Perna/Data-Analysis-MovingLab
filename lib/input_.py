#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 09:10:12 2021.

@author: michael
"""

# Project folder
database = './DataBase'
results = './res/data/'

# Zones
open_sky = '.maps/areas_of_interest/zone5.shp'
city_NS = 'maps/areas_of_interest/zone2.shp'
city_EW = '.maps/areas_of_interestzone3.shp'
old_city = '.maps/areas_of_interest/zone1.shp'
peripheric = '.maps/areas_of_interest/zone4.shp'

zone_dict = {open_sky: 'open_sky',
             city_NS: 'city_NS',
             city_EW: 'city_EW',
             old_city: 'old_city',
             peripheric: 'peripheric'}

# Lines of references
rail_forth = './maps/railways/foward_track_adjusted.shp'
rail_back = './maps/railways/backward_track_adjusted.shp'

fileTheo5a = './data/theodolites/trajectoire_5_st1.txt'
fileTheo5b = './data/theodolites/trajectoire_5_st2.txt'

# Loop shapefile
loop_shp = './maps/railways/loops.shp'
