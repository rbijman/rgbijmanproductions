# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 10:26:18 2025

@author: rbijman
"""

import pandas as pd
import numpy as np
import datetime
import requests


def call_AIWeerFileAPI(base,function_call,query):
    total_base = base+function_call
    response = requests.get(total_base + query)
    data = response.json()
    return data

def collect_and_clean_AIweerfiledata(start_date,end_date,ampm_border,shortlong_border):
    #%% load raw data
    dfs = pd.DataFrame()
    year = 2024
    for month in range(1,13,1):
        url = ('https://downloads.rijkswaterstaatdata.nl/filedata/{}-{:02d}_rws_filedata.csv').format(year,month)
        df_temp = pd.read_csv(url,sep=';')
        dfs = pd.concat([dfs, df_temp], axis=0,ignore_index=True)
    data = dfs

    #%%Create cleaned dataset
    datac = pd.DataFrame()
    datac[['NLSitNummer','Road','direction','Oorzaak_1','Oorzaak_2','Oorzaak_3','Oorzaak_4','traject']] = data[["NLSitNummer","RouteOms","hectometreringsrichting",'Oorzaak_1','Oorzaak_2','Oorzaak_3','Oorzaak_4','TRAJECTVILD']]

    datac['DateTimeStart'] = pd.to_datetime(data.DatumFileBegin+' ' + data.TijdFileBegin)
    datac['DateTimeEnd'] = pd.to_datetime(data.DatumFileEind+' ' + data.TijdFileEind)
    datac['datetime_rounded'] = datac.DateTimeStart.dt.round('60min')
    datac['Duration'] = data.FileDuur.str.replace(',','.').astype('float64')
    datac['weekday'] = datac.DateTimeStart.dt.dayofweek.astype('category')
    datac['month'] = datac.DateTimeStart.dt.month.astype('category')

    datac['HPstart'] = data.HectometerKop.str.replace(',','.').astype('float64')
    datac['HPend'] = data.HectometerStaart.str.replace(',','.').astype('float64')
    datac['distance'] = abs(datac.HPstart-datac.HPend)
    datac['GemLengte'] = data.GemLengte.str.replace(',','.').astype('float64')/1000
    datac[['trajectA','trajectB']] = datac['traject'].str.split(' - ',n=1,expand=True)

    #Find the lat_lon_coordinates per city 
    lat_lon_df = __get_lat_lon_per_city(datac)
    datac['traject_city'] = datac.apply(lambda x: x.trajectA if x.trajectA in lat_lon_df.city.values else x.trajectB,axis=1)

    #Find the weather per city
    weather_per_city = __get_weather_per_city(lat_lon_df, ["temperature_2m","rain","snowfall","precipitation","wind_speed_10m","direct_radiation","sunshine_duration"],start_date,end_date)

    # add weather information
    datac = pd.merge(left=datac,right=weather_per_city,left_on=['traject_city','datetime_rounded'],right_on=['city','date'],how='left')

    #add categories
    datac['ampm'] = datac.DateTimeStart.dt.time.apply(lambda x: 'am' if x<datetime.time(ampm_border) else 'pm')
    datac['shortlong'] = datac.Duration.apply(lambda x: 'short' if x<shortlong_border else 'long')
    datac['coldwarm'] = datac.temperature_2m.apply(lambda x: 'cold' if x<10 else 'warm')
    datac['rainydry'] = datac.rain.apply(lambda x: 'rainy' if x>1 else 'dry')
    datac['temp_cat'] = pd.qcut(datac.temperature_2m,q=[0,0.2,0.4,0.6,0.8,1],labels=['freezing','cold','comfortable','warm','hot'])

    print("Data collection and cleaning done!")

    return datac, lat_lon_df, weather_per_city

def update_sql_database(working_dir,AIweerfile_functions,data_to_update,sql_table_name):
    from sqlalchemy import create_engine
    pysql = __import_python_sql_class(working_dir)
    my_pypg = pysql(working_dir + r"\database_config.ini",'postgresql')
    engine = create_engine(f"postgresql+psycopg2://{my_pypg.db_info['user']}:{my_pypg.db_info['password']}@{my_pypg.db_info['host']}:{my_pypg.db_info['port']}/{my_pypg.db_info['dbname']}")
    data_to_update.to_sql(sql_table_name, engine, if_exists='replace')
    print("SQL database updated")

def update_pickle_with_sql_database_data(AIweerfile_functions,working_dir,pickle_file_path,sql_table_name):
    import os
    import time
    
    pysql = __import_python_sql_class(working_dir)
    my_pypg = pysql(working_dir + r"\database_config.ini",'postgresql')
    
    data = my_pypg.generic_get_query(f"SELECT * FROM {sql_table_name}")
    data.to_pickle(pickle_file_path)
    print(f'{pickle_file_path} updated')
    last_update = ('last_update done: {}').format(time.ctime(os.path.getmtime(pickle_file_path)))
    print_message = pickle_file_path + ' updated' + '/n' + last_update
    return print_message

def getHPrange(beginHP,endHP):
    if endHP>beginHP:
        return np.arange(beginHP,endHP,0.1).round(2)
    else:
        return np.arange(endHP,beginHP,0.1).round(2)
    
#%% private methods
def __get_lat_lon_per_city(datac):
    cities = []
    lat = []
    lon = []
    unique_city = pd.concat([datac.trajectA,datac.trajectB]).unique()
    for city in unique_city:
        if not city in cities:
            try:            
                lat_temp,lon_temp = __get_lat_lon(city.lower())

                lat.append(lat_temp)
                lon.append(lon_temp)
                cities.append(city)
                print(city)
            except:
                print(("{} NOT AVAILABLE").format(city))
                pass
            
    lat_lon_df = pd.DataFrame({'city':cities,'lat':lat,'lon':lon})
    lat_lon_df['lat'] = lat_lon_df.lat.astype('float')
    lat_lon_df['lon'] = lat_lon_df.lon.astype('float')
    return lat_lon_df

def __get_lat_lon(your_loc):
    import requests

    result_city = requests.get(url='https://geocoding-api.open-meteo.com/v1/search?name=' + your_loc)
    location = result_city.json()

    lat = str(list(filter(lambda city: city['country_code']=='NL',location['results']))[0]['latitude'])
    lon = str(list(filter(lambda city: city['country_code']=='NL',location['results']))[0]['longitude'])
    return(lat,lon) 

def __get_weather_per_city(lat_lon_df,weather_type,start_date,end_date):
    om = __cache_temp_data()
    weather_per_city_temp = __get_weather_from_api(om,lat_lon_df.lat.astype('str').to_list(), lat_lon_df.lon.astype('str').to_list(), start_date, end_date, lat_lon_df.city,weather_type)
    weather_per_city = weather_per_city_temp.reset_index().merge(lat_lon_df,left_on='city',right_on='city')
    return weather_per_city

   

def __get_weather_from_api(om,lat,long,start_date,end_date,cities,weather_types):
    city_df = pd.DataFrame()

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
    	"latitude": lat,
    	"longitude": long,
    	"start_date": start_date,
    	"end_date": end_date,
    	"hourly": weather_types
    }
    responses = om.weather_api(url, params=params)
    
    # Process first location. Add a for-loop for multiple locations or weather models
    for idx1, response in enumerate(responses):
        frames = []
        for idx2,weather_type in enumerate(weather_types):

            # Process hourly data. The order of variables needs to be the same as requested.
            hourly = response.Hourly()
            hourly_weather_type = hourly.Variables(idx2).ValuesAsNumpy()
            
            hourly_data = {"date": pd.date_range(
            	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            	freq = pd.Timedelta(seconds = hourly.Interval()),
            	inclusive = "left"
            )}
            
            hourly_data[weather_types[idx2]] = hourly_weather_type
            
            hourly_dataframe = pd.DataFrame(data = hourly_data)
            hourly_dataframe.date = hourly_dataframe.date.dt.tz_convert(None)
            hourly_dataframe.set_index('date',inplace=True)
            frames.append(hourly_dataframe)
            weather_type_df = pd.concat(frames,axis=1)
            weather_type_df['city'] = cities[idx1]
        city_df = pd.concat([city_df,weather_type_df],axis=0)

    if len(lat)>1 or len(weather_types)>1:
        return city_df
    else:
        return hourly_dataframe





def __cache_temp_data():

    import openmeteo_requests
    import requests_cache
    from retry_requests import retry

    # Setup the Open-Meteo API client with a cache and retry mechanism
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    om = openmeteo_requests.Client(session=retry_session)
    
    return om

def __import_python_sql_class(working_dir):
    import sys
    sys.path.insert(0,working_dir + r"\SQL")
    from python_postgress_class import python_postgres as pypg
    return pypg