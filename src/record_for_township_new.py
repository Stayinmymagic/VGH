# -*- coding: utf-8 -*-
"""
Created on Sun Jul 11 16:56:54 2021

@author: notfu
"""

import datetime as dt
import pickle
import math
import statistics
import numpy as np
import pandas as pd
from dateutil import parser
from datetime import datetime
#%%
##打開全台灣郵遞區號所對應的空測站
with open('zip_fit_station.pickle' ,'rb') as file:
    zip_fit_station = pickle.load(file)
#%%全台灣空測站站名
with open('StationList.pickle' ,'rb') as file:
    Station = pickle.load(file)

Station[44] = '台東'
Station[50] = '台南'
Station[51] = '台西'
Station.append('富貴角')
#%%
def get_five_stations(near_stations):
    global all_year_data
    stations_dict = {}
    for i in near_stations:
        stations_dict[i[0]] = all_year_data[i[0]]
    return stations_dict
#從特定日期往回推取一年資料
index_list = ['CO','NO2','O3', 'PM10','PM2.5','SO2']
def get_past_record (index_date,past1y_date):
    record = {}
    for i in index_list:
        temp_index_date = index_date
        record[i] = {}
        while temp_index_date != past1y_date:
            date_dict = temp_index_date.strftime("%Y/%m/%d")
            record[i][date_dict] = {}
            temp_index_date = temp_index_date - dt.timedelta(days=1)
    return record

def LinearInterpolation(con_val,distValues):
    val=0
    used_dist=[]
    used_val = []
    ioi = [] #index of intrested, max is 3
    station_count = 0
    for idx in range(len(distValues)):
        voi = con_val[idx]
        if voi != None and math.isnan(voi) == False:
            used_dist.append(distValues[idx])
            used_val.append(voi)
            ioi.append(idx)
            station_count+=1
        if station_count >= 3:
            break
    cumulated_distance = 0
    for d in used_dist:
        cumulated_distance += 1/d
    for idx in ioi:
        val += con_val[idx]*(1/distValues[idx])
    result_val = 0.0
    try:
        result_val = round(val/cumulated_distance,5)
    except ZeroDivisionError:#除零錯誤
       result_val = np.nan
    return result_val

def calculate_zip_index_value(delta, index_date,patient_stations,patient_database,patient_3y_record):
    day = index_date
    for i in range(delta):
        date = day.strftime("%Y/%m/%d")
        for index in index_list:
            for hr in range(24):
                index_data = []
                index_station = []
                for station in patient_stations:
                    try: 
                        if patient_database[station[0]][date] != {}:
                            
                            if patient_database[station[0]][date][index] != {}:
                                value = patient_database[station[0]][date][index][hr]
                                if value != None:
                                    
                                    index_data.append(value)
                                    index_station.append(station[1])
#                                else:
#                                    print(station,date,index,hr, value)
             
                              
                    except KeyError:#有時空測站會少某日的紀錄
                        continue
                ##應該是index_data!=[]才執行interpolation
                if index_data != []:
                    patient_3y_record[index][date][hr] = LinearInterpolation(index_data,index_station)
                else:
                    patient_3y_record[index][date][hr] = np.nan

        day = day - dt.timedelta(days=1)
    return patient_3y_record

#%%
iaqi_dict = {'CO': [0, 4.4, 9.4, 12.4, 15.4, 30.4, 40.4, 50.4],
       'NO2': [0, 53, 100, 360, 649, 1249, 1649, 2049],
       'O3': [0, 55, 70, 125, 164, 204, 404, 504, 604],
       'PM10': [0, 54, 125, 254, 354, 424, 504, 604],
       'PM2.5': [0, 15.4, 35.4, 54.4, 150.4, 250.4, 350.4, 500.4],
       'SO2': [0, 35, 75, 185, 304, 604, 804, 1004]
      }
iaqi_level_val = [0, 50,100, 150, 200, 300, 400, 500]
def calculate_aqi(Cp, itype):
    val = 0.0
    bp_high = 0
    bp_low = 0
    iaqi_high = 0
    iaqi_low = 0

    for idx in range(6):
        if Cp > iaqi_dict[itype][idx]:
            bp_high = iaqi_dict[itype][idx+1]
            bp_low = iaqi_dict[itype][idx]
            iaqi_high = iaqi_level_val[idx+1]
            iaqi_low = iaqi_level_val[idx]

    if bp_high-bp_low != 0:
        val = round((iaqi_high-iaqi_low) / (bp_high-bp_low) * (Cp - bp_low) +iaqi_low, 5)
    return val
#%% aqi in each hour
def calculate_aqi_each_hour(iaqi_patient_3y_record):
    aqi_patient_3y_record ={}
    for day in iaqi_patient_3y_record['CO'].keys():
        aqi_patient_3y_record[day]={}
    for day in aqi_patient_3y_record.keys():
        for hr in range(24):
            aqi_index_each_hour = []
            for i in index_list:
                aqi_index_each_hour.append(iaqi_patient_3y_record[i][day][hr])
            aqi_patient_3y_record[day][hr] = np.nanmax(aqi_index_each_hour)
    return aqi_patient_3y_record

# iaqi in Each hour
def calculate_iaqi_each_hour(index_date,patient_3y_record):
    iaqi_patient_3y_record ={}
    for i in index_list:
        iaqi_patient_3y_record[i] = {}
        for day in patient_3y_record[i].keys():
            iaqi_patient_3y_record[i][day] = {}
    
    for index in index_list:
        for day in patient_3y_record[i].keys():
            for hr in range(24): 
                if np.isnan(patient_3y_record[index][day][hr]) == False:                    
                    temp_iaqi = calculate_aqi(patient_3y_record[index][day][hr], i)
                    iaqi_patient_3y_record[index][day][hr] = temp_iaqi
                else:
                    iaqi_patient_3y_record[index][day][hr] = np.nan
    return iaqi_patient_3y_record

#%%
final_calculate_list = ['CO_max', 'CO_mean','CO_min','iaqi_max_CO', 'iaqi_mean_CO',  'iaqi_min_CO','CO_0to50','CO_50to100','CO_100to150','CO>150','NO2_max', 
                          'NO2_mean', 'NO2_min','iaqi_max_NO2', 'iaqi_mean_NO2',  'iaqi_min_NO2', 'NO2_0to50','NO2_50to100','NO2_100to150','NO2>150','O3_max', 
                          'O3_mean','O3_min','iaqi_max_O3','iaqi_mean_O3','iaqi_min_O3','O3_0to50','O3_50to100','O3_100to150','O3>150','PM10_max',
                          'PM10_mean','PM10_min','iaqi_max_PM10','iaqi_mean_PM10','iaqi_min_PM10', 'PM10_0to50','PM10_50to100','PM10_100to150','PM10>150',
                          'PM2.5_max','PM2.5_mean','PM2.5_min','iaqi_max_PM2.5','iaqi_mean_PM2.5','iaqi_min_PM2.5', 'PM2.5_0to50','PM2.5_50to100','PM2.5_100to150','PM2.5>150',
                          'SO2_max','SO2_mean','SO2_min','iaqi_max_SO2','iaqi_mean_SO2','iaqi_min_SO2', 'SO2_0to50','SO2_50to100','SO2_100to150','SO2>150',
                        'continues_expose_hr','max_aqi','mean_aqi','min_aqi','0to50','50to100','100to150','aqi>150']
#%%
def get_final_record(patient_3y_record,iaqi_patient_3y_record,aqi_patient_3y_record): 
    final_record = []
    #final_record.append(town)
    for index in index_list:
        index_all_values = []
        index_all_values_iaqi = []
        
        for day in patient_3y_record[index].keys():
            index_all_values += list(patient_3y_record[index][day].values())
        final_record.append(max(index_all_values))
        final_record.append(round(np.nanmean(index_all_values),3))
        final_record.append(min(index_all_values))
        for day in iaqi_patient_3y_record[index].keys():
            index_all_values_iaqi += list(iaqi_patient_3y_record[index][day].values())
        final_record.append(max(index_all_values_iaqi))##就是將上面算出來的值轉換成aqi
        final_record.append(round(np.nanmean(index_all_values_iaqi),3))
        final_record.append(min(index_all_values_iaqi))
        final_record.append(len([i for i in index_all_values_iaqi if i < 50]))
        final_record.append(len([i for i in index_all_values_iaqi if i >= 50 and i < 100]))
        final_record.append(len([i for i in index_all_values_iaqi if i >= 100 and i < 150]))
        final_record.append(len([i for i in index_all_values_iaqi if i >= 150 ]))
    index_all_values_aqi = []
    for day in aqi_patient_3y_record.keys():
        index_all_values_aqi  += list(aqi_patient_3y_record[day].values())
    ##print(index_all_values_aqi)
    ##countinue expose hrs
    max_aqi_hrs = 0
    count = 0
    for i in index_all_values_aqi:
        if i > 150:
            count+=1
        else:
            if count > max_aqi_hrs:
                max_aqi_hrs = count
                count = 0      
    final_record.append(max_aqi_hrs)   
    final_record.append(max(index_all_values_aqi))
    final_record.append(round(np.nanmean(index_all_values_aqi),5))
    final_record.append(min(index_all_values_aqi))

    final_record.append(len([i for i in index_all_values_aqi if i < 50]))
    final_record.append(len([i for i in index_all_values_aqi if i >= 50 and i < 100]))
    final_record.append(len([i for i in index_all_values_aqi if i >= 100 and i < 150]))
    final_record.append(len([i for i in index_all_values_aqi if i >= 150 ]))
    return final_record  

            
#%%合併2018-2021pickle
all_year_data = {}
for i in Station:
    all_year_data[i] = {}
for year in range(2018, 2022):
    print(year)    
    with open('processed_%s.pickle'%str(year) ,'rb') as file:
        annual_data = pickle.load(file)
    for j in all_year_data.keys():
        all_year_data[j] = {**all_year_data[j], **annual_data[j]}##merge two dict
#%%參數
town_list = zip_fit_station.keys()
start = datetime.strptime('2019/01/01', '%Y/%m/%d')
end = datetime.strptime('2021/06/30', '%Y/%m/%d')
delta = dt.timedelta(days=365)
#%%
for town in town_list:
    final_table = pd.DataFrame(columns = final_calculate_list)
    near_stations = zip_fit_station[town]#取得5個鄰近空氣監測站
    five_stations_data = get_five_stations(near_stations)
    for index in range((end - start).days):
        index_date = start + dt.timedelta(days = (index-1))
        past1y_date = index_date - delta
        record = get_past_record(index_date, past1y_date)
        record = calculate_zip_index_value(365, index_date,near_stations,five_stations_data,record)
        iaqi_record = calculate_iaqi_each_hour(index_date, record )
        aqi_record = calculate_aqi_each_hour(iaqi_record)
        final_record = pd.Series(get_final_record(record,iaqi_record,aqi_record), name = index_date, index = final_calculate_list )
        final_table = final_table.append(final_record, ignore_index=False)

    final_table.to_csv('%s.csv'%int(town))
    print(town)    
    
#%%
print(zip_fit_station[253.0][0][0])       