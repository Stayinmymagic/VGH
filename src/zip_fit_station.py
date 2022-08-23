#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 11:16:29 2020

@author: notfunny6889
"""

import operator
import pickle
import math

with open("data/stationList.pickle", "rb") as f:
    station_list = pickle.load(f)
with open("data/station_location_dict.pickle", "rb") as f:
    station_location_dict = pickle.load(f)
with open("data/center_of_postcode_dict.pickle", "rb") as f:
    center_of_postcode_dict = pickle.load(f)
with open("data/location_dict.pickle", "rb") as f:
    location_dict = pickle.load(f)
    
#%%
station_location_dict['台東'] = station_location_dict.pop('臺東')
station_location_dict['台南'] = station_location_dict.pop('臺南')
station_location_dict['台西'] = station_location_dict.pop('臺西')
#%%
def near_station(post_code):
    result = {}
    hospital_loc = center_of_postcode_dict[post_code]
    distance_dict = {}
    for station in station_location_dict:
        sta_loc = station_location_dict[station]

        distance = math.sqrt((hospital_loc[0]-sta_loc[0])**2+(hospital_loc[1]-sta_loc[1])**2)
        distance_dict[station] = round(distance,5)
    sorted_dist = sorted(distance_dict.items(), key=operator.itemgetter(1))
    result = sorted_dist[:5]
    return result

#%%
zip_fit_station={}
for i in center_of_postcode_dict.keys():
    zip_fit_station[i] = near_station(i)
#%%
zip_fit_station[104.0] = zip_fit_station.pop(10491.0)
#%%
print(zip_fit_station[10491.0])
#%%
with open('zip_fit_station.pickle' ,'wb') as file:
    pickle.dump(zip_fit_station, file, protocol=pickle.HIGHEST_PROTOCOL)    