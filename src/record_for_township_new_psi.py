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
index_list = ['CO','NO2','O3', 'PM10','SO2']
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
final_psi_indices = ['zip_code','CO_max', 'CO_mean','CO_min','ipsi_max_CO', 'ipsi_mean_CO', 'ipsi_min_CO','CO_0to50','CO_50to100','CO>100','NO2_max', 
                          'NO2_mean', 'NO2_min','ipsi_max_NO2', 'ipsi_mean_NO2',  'ipsi_min_NO2', 'NO2_0to50','NO2_50to100','NO2>100','O3_max', 
                          'O3_mean','O3_min','ipsi_max_O3','ipsi_mean_O3','ipsi_min_O3','O3_0to50','O3_50to100','O3>100','PM10_max',
                          'PM10_mean','PM10_min','ipsi_max_PM10','ipsi_mean_PM10','ipsi_min_PM10', 'PM10_0to50','PM10_50to100','PM10>100',
                          'SO2_max','SO2_mean','SO2_min','ipsi_max_SO2','ipsi_mean_SO2','ipsi_min_SO2', 'SO2_0to50','SO2_50to100','SO2>100',
                        'continues_expose_hr','max_psi','mean_psi','min_psi','0to50','50to100','psi>100']
#%%
ipsi_level_val = [0, 50, 100, 200, 300, 500]
ipsi_dict = {'CO': [0, 4.5, 9, 15, 30, 40, 50],
       'NO2': [0, 0, 0, 600, 1200, 1600, 2000],
       'O3': [0, 60,120, 200, 400, 500, 600],
       'PM10': [0, 50, 150, 350, 420, 500, 600],
       'SO2': [0, 30, 140, 300, 600, 800, 1000]
      }
def calculate_psi(Cp, itype):
    val = 0.0
    bp_high = 0
    bp_low = 0
    ipsi_high = 0
    ipsi_low = 0

    for idx in range(5):
        if Cp > ipsi_dict[itype][idx]:
            bp_high = ipsi_dict[itype][idx+1]
            bp_low = ipsi_dict[itype][idx]
            ipsi_high = ipsi_level_val[idx+1]
            ipsi_low = ipsi_level_val[idx]
            break

    if bp_high-bp_low != 0:
        val = round((ipsi_high-ipsi_low) / (bp_high-bp_low) * (Cp - bp_low) +ipsi_low,5)
    return val
#%% iaqi in Each hour
def calculate_ipsi_each_hour(index_date,patient_3y_record):
    ipsi_patient_3y_record ={}
    for i in index_list:
        ipsi_patient_3y_record[i] = {}
        for day in patient_3y_record[i].keys():
            ipsi_patient_3y_record[i][day] = {}
    
    for index in index_list:
        for day in patient_3y_record[i].keys():
            for hr in range(24):
                if np.isnan(patient_3y_record[index][day][hr]) == False:                    
                    temp_ipsi = calculate_psi(patient_3y_record[index][day][hr], i)
                    ipsi_patient_3y_record[index][day][hr] = temp_ipsi
                else:
                    ipsi_patient_3y_record[index][day][hr] = np.nan
    return ipsi_patient_3y_record
        
#%% aqi in each hour
def calculate_psi_each_hour(ipsi_patient_3y_record):
    psi_patient_3y_record ={}
    for day in ipsi_patient_3y_record['CO'].keys():
        psi_patient_3y_record[day]={}
    for day in psi_patient_3y_record.keys():
        for hr in range(24):
            psi_index_each_hour = []
            for i in index_list:
                psi_index_each_hour.append(ipsi_patient_3y_record[i][day][hr])
            psi_patient_3y_record[day][hr] = np.nanmax(psi_index_each_hour)
    return psi_patient_3y_record
#%%
def get_final_record(patient_3y_record,ipsi_patient_3y_record,psi_patient_3y_record): 
    final_record = []
    #final_record.append(patient_zipcode)
    for index in index_list:
        index_all_values = []
        index_all_values_ipsi = []
        for day in patient_3y_record[index].keys():
            index_all_values += list(patient_3y_record[index][day].values())
        final_record.append(max(index_all_values))
        final_record.append(round(np.nanmean(index_all_values),3))
        final_record.append(min(index_all_values))
        for day in ipsi_patient_3y_record[index].keys():
            index_all_values_ipsi += list(ipsi_patient_3y_record[index][day].values())
        final_record.append(max(index_all_values_ipsi))##就是將上面算出來的值轉換成aqi
        final_record.append(round(np.nanmean(index_all_values_ipsi),3))
        final_record.append(min(index_all_values_ipsi))
        final_record.append(len([i for i in index_all_values_ipsi if i < 50]))
        final_record.append(len([i for i in index_all_values_ipsi if i >= 50 and i < 100]))
        final_record.append(len([i for i in index_all_values_ipsi if i >= 100]))
    index_all_values_psi = []
    for day in psi_patient_3y_record.keys():
        index_all_values_psi  += list(psi_patient_3y_record[day].values())
    ##countinue expose hrs
    max_psi_hrs = 0
    count = 0
    for i in index_all_values_psi:
        if i > 150:
            count+=1
        else:
            if count > max_psi_hrs:
                max_psi_hrs = count
                count = 0      
    final_record.append(max_psi_hrs)        
    final_record.append(max(index_all_values_psi))
    final_record.append(round(np.nanmean(index_all_values_psi),5))
    final_record.append(min(index_all_values_psi))
            
    final_record.append(len([i for i in index_all_values_psi if i < 50]))
    final_record.append(len([i for i in index_all_values_psi if i >= 50 and i < 100]))
    final_record.append(len([i for i in index_all_values_psi if i >= 100]))
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
    final_table = pd.DataFrame(columns = final_psi_indices)
    near_stations = zip_fit_station[town]#取得5個鄰近空氣監測站
    five_stations_data = get_five_stations(near_stations)
    for index in range((end - start).days):
        index_date = start + dt.timedelta(days = (index-1))
        past1y_date = index_date - delta
        record = get_past_record(index_date, past1y_date)
        record = calculate_zip_index_value(365, index_date,near_stations,five_stations_data,record)
        ipsi_record = calculate_ipsi_each_hour(index_date, record )
        psi_record = calculate_psi_each_hour(ipsi_record)
        final_record = pd.Series(get_final_record(record,ipsi_record,psi_record), name = index_date, index = final_psi_indices)
        final_table = final_table.append(final_record, ignore_index=False)

    final_table.to_csv('%s.csv'%int(town))
    print(town)    
    
#%%
print(zip_fit_station[253.0][0][0])       