import pandas as pd
import numpy as np
from datetime import datetime,date, time 
import os
import io
import requests
import glob

os.chdir(r'D:\Users\Sanja\Desktop\Air_Pollution')

#CREATE DATAFRAME

#codebook for component and stations 
component=pd.read_csv(r'D:\Users\Sanja\Desktop\Air_Pollution\Data\component.csv',delimiter=',') 
station=pd.read_csv(r'D:\Users\Sanja\Desktop\Air_Pollution\Data\stations.csv',delimiter=',')

#import real time data from url
url_2019=" https://data.gov.rs/en/datasets/r/a8f71ec0-0a68-4d4f-8f37-ceabdcb98569"
s=requests.get(url_2019).content
air=pd.read_csv(io.StringIO(s.decode('utf-8')))

#merge air dataframe with component codebook in order to get information about component name under component_id
air_c=pd.merge(air, component,  how='left', left_on=['component_id'], right_on = ['id'])
#merge air_c (dataframe with name of components) with station information book in order to get information about station under station_id
air_c_s=pd.merge(air_c,station,how='left', left_on=['station_id'], right_on = ['id'])


#ARRANGE DATAFRAME

#Create separated Day/Hour columns from date_time column
air_c_s['date_time']=pd.to_datetime(air_c_s['date_time'])
air_c_s['Day']=[d.date() for d in air_c_s['date_time']]
air_c_s['Hour']=[d.time().strftime('%H') for d in air_c_s['date_time']]


#Create final df for furter usage, extract columns of interest and assign appropriate names
air_pollution=air_c_s[['Day','Hour','component_id','k_short_name', 'value','k_unit_ebas','station_id','k_name_y','k_city','latitude', 'longitude']]
air_pollution.columns=['Day','Hour','Component_ID','Component_Name','Value','Unit','Station_ID','Station_Name','Station_City','Latitude','Longitude']

#in final representation only component in list_components will be used 
#[SO2, PM10, O3, NO2, CO, PM2.5]
list_component=[1,5,7,8,10,6001] 
air_pollution=air_pollution.loc[air_pollution['Component_ID'].isin(list_component),:]

#round values on wo decimal places
air_pollution['Value']=air_pollution['Value'].round(2)

#drop rows where we do not have information about Station
air_pollution.dropna(subset=['Station_Name','Station_City'],inplace=True)

print(air_pollution.tail(10))
#save data into realtime 
air_pollution.to_csv(r'D:\Users\Sanja\Desktop\Air_Pollution\air_pollution_realtime.csv')

