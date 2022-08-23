#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 12:51:41 2020

@author: notfunny6889
"""

import os
import pickle
import pandas as pd
import re
import glob
#%%

with open('StationList.pickle' ,'rb') as file:
    Station = pickle.load(file)
#%%
Station[44] = '台東'
Station[50] = '台南'
Station[51] = '台西'
#%%
Station.append('富貴角')
#%% 空測站和空品區的dict
df_station = pd.read_csv('空氣品質監測站.csv')

#%%
Area = ['中部空品區','北部空品區','竹苗空品區','宜蘭空品區','花東空品區','高屏空品區','雲嘉南空品區','離島監測站']
dict_station = {}
for i in Area:
    dict_station[i] = []
#%%
for i in df_station.index:
    dict_station[df_station['空品區'][i]].append(df_station['測站名稱'][i])
  
#%%
itemList = ['PM10', 'PM2.5', 'NO2', 'CO', 'SO2', 'O3']
#%%2019所有空測站value的dict
dict_final = {}
for i in Station:
    dict_final[i] = {}
#%%
df_station = df_station.drop(13)
#%%
##create each station's nested dict(2011-2020)
itemList = ['PM10', 'PM2.5', 'NO2', 'CO', 'SO2', 'O3']
def Create_each_dict(file):
    
    dict_all = {}
    date = file['日期'].unique().tolist()
    for i in range(len(date)):
        date[i] = date[i][:10]
    time = [i for i in range(24)]
    for i in date:
        dict_all[i] = {}
    for date in dict_all:    
        for index in itemList :
            dict_all[date][index] = {}
    for i in file.index:
        for item in itemList:
            if re.sub(r"\s+", "", file['測項'][i]) == item:
                index = re.sub(r"\s+", "", file['測項'][i])
                datetime = file['日期'][i][:10]
                value = list(file.iloc[i,3:27])
                for v in range(24):
                    try:
                        value[v] = float(value[v])
                    except ValueError:
                        value[v] = None
                dict_all[datetime][index]=dict(zip(time, value))
    return dict_all
#%%
##create each station's nested dict(2021)
def Create_dict_2021(df, station):
    global Station
    dict_final = {}
    dict_all = {} 
    date = df['MonitorDate'].unique().tolist()
    time = [i for i in range(24)]
    for i in date:
        i = i.replace('-', '/')
        dict_all[i] = {}
    for date in dict_all:    
        for index in itemList :
            dict_all[date][index] = {}
    sector = df.groupby("SiteName")
#    for station in Station:

    station_sector = sector.get_group(station)
    station_sector = station_sector.reset_index()

    for i in station_sector.index:
    #for i in range(24):
        for item in itemList:
            if station_sector['ItemEngName'][i] == item:
                index = station_sector['ItemEngName'][i]
                datetime = station_sector['MonitorDate'][i]
                datetime = datetime.replace('-', '/')
                value = list(station_sector.loc[i][8:32])
                #print(value)
                for v in range(24):
                    try:
                        value[v] = float(value[v])
                    except ValueError:
                        value[v] = None
                dict_all[datetime][item] = dict(zip(time, value))
                #print(station, ' ', datetime, ' ', item, ' ', dict_all[datetime][item])
                
        
        #dict_final[station] = dict_all
        #print(dict_final[station])
    return dict_all
#%% 開啟xls檔
for area in Area:
    for station in dict_station[area]:
        file = pd.read_excel('107年 %s/107年%s站_20190315.xls'%(area,station))
        print(area)
        dict_all = Create_each_dict(file)
        dict_final[station] = dict_all

#%% 開啟csv檔_2019
for area in Area:
    for station in dict_station[area]:
        file = pd.read_csv('%s/%s_2019.csv'%(area, station),encoding = 'ansi')
        for col in file.columns:           
            file = file.rename(columns = {col:re.sub(r"\s+", "", col)})
        print(station)
        file = file.drop([0]) 
        dict_all = Create_each_dict(file)
        dict_final[station] = dict_all
#%% 開啟csv檔_2020
for area in Area:
    for station in dict_station[area]:
        file = pd.read_csv('%s_2020.csv'%(station),encoding = 'ansi')
        for col in file.columns:           
            file = file.rename(columns = {col:re.sub(r"\s+", "", col)})
        print(station)
        file = file.drop([0])
        dict_all = Create_each_dict(file)
        dict_final[station] = dict_all
#%%開啟csv檔_2021

dirpath = r"D:\Downloads\VGH\excelRaw\全部_2021\*\*.csv"
all_file_path = glob.glob(dirpath)
df = pd.DataFrame()
for file_path in all_file_path:
    file = pd.read_csv(r"%s"%file_path,encoding = 'utf-8')
    df = pd.concat([df, file], axis = 0, ignore_index=True)
#%%
dict_final = {}
for i in Station:
    dict_all = Create_dict_2021(df, i)
    dict_final[i] = dict_all
#%%
dict_final['台西'] = dict_final.pop('臺西')
#%%dict to pickle
with open('processed_2021.pickle' ,'wb') as file:
    pickle.dump(dict_final, file, protocol=pickle.HIGHEST_PROTOCOL)
#%%
with open('zip_fit_station.pickle', 'rb') as file:
    test = pickle.load(file)
#%%
for station in test.keys():
    for day in test[station].keys():
        for index in test[station][day].keys():
            for hr in test[station][day][index].keys():
                if test[station][day][index][hr] != None :
                    if test[station][day][index][hr] > 1000:
                        print(station, day,index, hr,test[station][day][index][hr] )
#%%
l = ['a', 'b']
d = {}


for i in range(len(l)):
    v = {1:12, 2:24+i}
    d[l[i]] = v
  

