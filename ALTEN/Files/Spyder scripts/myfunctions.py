# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 10:26:18 2025

@author: rbijman
"""

import pandas as pd

def get_lat_lon_per_city(datac):
    cities = []
    lat = []
    lon = []
    unique_city = pd.concat([datac.trajectA,datac.trajectB]).unique()
    for city in unique_city:
        if not city in cities:
            try:            
                # lat_temp,lon_temp = get_lat_lon_photon(city.lower())
                lat_temp,lon_temp = get_lat_lon_new(city.lower())

                lat.append(lat_temp)
                lon.append(lon_temp)
                cities.append(city)
                print(city)
            except:
                print(("{} failed").format(city))
                pass
            
    lat_lon_df = pd.DataFrame({'city':cities,'lat':lat,'lon':lon})
    lat_lon_df['lat'] = lat_lon_df.lat.astype('float')
    lat_lon_df['lon'] = lat_lon_df.lon.astype('float')
    return lat_lon_df


def get_weather_type_per_trafic(weather_type_per_city,time,loc):
    try:
        index = weather_type_per_city.date.searchsorted(time)  
        weather_type = weather_type_per_city.loc[index,loc]
    except:
        weather_type = None
    return weather_type

def get_weather_per_city(om,lat,lon,cities,weather_type):
    
    start_date = '2024-01-01'
    end_date = '2024-12-31'

    b = get_weather_from_api(om,lat, lon, start_date, end_date, cities,weather_type)
    return b

def get_weather_per_city2(om,lat_lon_df,weather_type):
    
    start_date = '2024-01-01'
    end_date = '2024-12-31'

    weather_per_city_temp = get_weather_from_api(om,lat_lon_df.lat.astype('str').to_list(), lat_lon_df.lon.astype('str').to_list(), start_date, end_date, lat_lon_df.city,weather_type)
    weather_per_city = weather_per_city_temp.T.merge(lat_lon_df,left_index=True,right_on='city').melt(id_vars=['city','lat','lon'],var_name='dateandtime',value_name=weather_type)
    weather_per_city.dateandtime = pd.to_datetime(weather_per_city.dateandtime)  
    return weather_per_city
    

    
def get_lat_lon_photon(your_loc):
    from geopy.geocoders import Photon
    
    app = Photon()
    
    location = app.geocode(your_loc).raw
    # return (location['lat'],location['lon'])
    return (str(location['geometry']['coordinates'][1]),str(location['geometry']['coordinates'][0]))

def get_lat_lon_new(your_loc):
    import requests

    result_city = requests.get(url='https://geocoding-api.open-meteo.com/v1/search?name=' + your_loc)
    location = result_city.json()

    lat = str(list(filter(lambda city: city['country_code']=='NL',location['results']))[0]['latitude'])
    lon = str(list(filter(lambda city: city['country_code']=='NL',location['results']))[0]['longitude'])
    return(lat,lon)    


# import openmeteo_requests
    
# import requests_cache as rc
import pandas as pd
# from retry_requests import retry
    

def get_weather_from_api(om,lat,long,start_date,end_date,cities,weather_types):
    frames = []

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
    for idx, response in enumerate(responses): #ADD INDEX HERE

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_weather_type = hourly.Variables(0).ValuesAsNumpy()
        
        hourly_data = {"date": pd.date_range(
        	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        	freq = pd.Timedelta(seconds = hourly.Interval()),
        	inclusive = "left"
        )}
        
        hourly_data[cities[idx]] = hourly_weather_type
        
        hourly_dataframe = pd.DataFrame(data = hourly_data)
        hourly_dataframe.date = hourly_dataframe.date.dt.tz_convert(None)
        hourly_dataframe.set_index('date',inplace=True)
        frames.append(hourly_dataframe)
    
    frames_df = pd.concat(frames,axis=1)
        
    if len(lat)>1:
        return frames_df
    else:
        return hourly_dataframe


def cache_temp_data():

    import openmeteo_requests
    import requests_cache
    from retry_requests import retry

    # Setup the Open-Meteo API client with a cache and retry mechanism
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    om = openmeteo_requests.Client(session=retry_session)
    
    return om

#%% No longer in use

# def get_lat_lon(your_loc):

#     from geopy.geocoders import Nominatim
#     # from pprint import pprint

#     # Instantiate a new Nominatim client
#     app = Nominatim(user_agent="tutorial")

#     # Get location raw data from the user
#     # your_loc = input("Enter your location: ")
#     location = app.geocode(your_loc).raw
#     return (location['lat'],location['lon'])
#     # Print raw data
#     # pprint(location)

# def get_temperature_per_trafic(om,location,date,time):
#     a = get_lat_lon_photon(location)

#     start_date = date
#     end_date = date
#     b = get_weather_from_api(om,a[0], a[1], start_date, end_date)
#     index = b.date.searchsorted(time.tz_localize('UTC'))  
#     return b.temperature_2m[index]
