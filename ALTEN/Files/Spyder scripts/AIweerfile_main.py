# -*- coding: utf-8 -*-

#%% import
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import AIweerfile_functions

#%% Variable defitions
shortlong_border = 20
ampm_border = 12
month_map = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
day_map = {0:'Mon',1:'Tue',2:'Wed',3:'Thu',4:'Fri',5:'Sat',6:'Sun'}
season_bins = [0,3,6,9,12]
season_names = ['winter','spring','summer','autumn']

#%% load data
data = pd.read_csv(r"C:\Users\rbijman\Documents\GitHub\rgbijmanproductions\ALTEN\Files\Data\2024-01_rws_filedata.csv",sep=';')
dfs = pd.DataFrame()
for year in range(1,13,1):
    df_temp = pd.read_csv((r"C:\Users\rbijman\Documents\GitHub\rgbijmanproductions\ALTEN\Files\Data\2024-{:02d}_rws_filedata.csv").format(year),sep=';')
    dfs = pd.concat([dfs, df_temp], axis=0,ignore_index=True)
data = dfs

#%%Create dataset to use for plots

def getHPrange(beginHP,endHP):
    if endHP>beginHP:
        return np.arange(beginHP,endHP,0.1).round(2)
    else:
        return np.arange(endHP,beginHP,0.1).round(2)

datac = pd.DataFrame(data["NLSitNummer"])
datac['DateTimeStart'] = pd.to_datetime(data.DatumFileBegin+' '+data.TijdFileBegin)
datac['DateTimeEnd'] = pd.to_datetime(data.DatumFileEind+' '+data.TijdFileEind)
datac['Duration'] = data.FileDuur.str.replace(',','.').astype('float64')
datac['Road'] = data.RouteOms#.astype('category')
datac['HPstart'] = data.HectometerKop.str.replace(',','.').astype('float64')
datac['HPend'] = data.HectometerStaart.str.replace(',','.').astype('float64')
datac['distance'] = abs(datac.HPstart-datac.HPend)
datac['direction'] = data.hectometreringsrichting;
datac['HPrange'] = datac.apply(lambda x: getHPrange(x['HPstart'],x['HPend']),axis=1)
datac['ampm'] = datac.DateTimeStart.dt.time.apply(lambda x: 'am' if x<datetime.time(ampm_border) else 'pm')
datac['shortlong'] = datac.Duration.apply(lambda x: 'short' if x<shortlong_border else 'long')
datac['month'] = data.DatumFileBegin.apply(lambda x: x[5:7]).astype(int).astype('category')
datac['date'] = datac.DateTimeStart.dt.date
datac['time'] = datac.DateTimeStart.dt.time
datac['season'] = pd.cut(datac.month,season_bins,right=True,labels=season_names)
datac['weekday'] = datac.DateTimeStart.dt.dayofweek
datac['traject'] = data.TRAJECTVILD
datac[['trajectA','trajectB']] = datac['traject'].str.split(' - ',n=1,expand=True)
datac['distance_rel'] = datac.distance.div(datac.groupby(by='Road').HPstart.transform('max'))
datac['datetime_rounded'] = datac.DateTimeStart.dt.round('60min')
datac[['Oorzaak_1','Oorzaak_2','Oorzaak_3','Oorzaak_4']] = data[['Oorzaak_1','Oorzaak_2','Oorzaak_3','Oorzaak_4']]

#Find the lat_lon_coordinates per city 
lat_lon_df = AIweerfile_functions.get_lat_lon_per_city(datac)
datac['traject_city'] = datac.apply(lambda x: x.trajectA if x.trajectA in lat_lon_df.city.values else x.trajectB,axis=1)

#Find the weather per city
om = AIweerfile_functions.cache_temp_data()
temperature_per_city = AIweerfile_functions.get_weather_per_city2(om, lat_lon_df,"temperature_2m")
rain_per_city = AIweerfile_functions.get_weather_per_city2(om, lat_lon_df,"rain") 
weather_per_city = pd.concat([temperature_per_city,rain_per_city.rain],axis=1)

#add temperature              
datac = pd.merge(left=datac,right=temperature_per_city,left_on=['traject_city','datetime_rounded'],right_on=['city','dateandtime'],how='left').drop(['dateandtime','city'],axis=1)
#add rain
datac = pd.merge(left=datac,right=rain_per_city[['city','dateandtime','rain']],left_on=['traject_city','datetime_rounded'],right_on=['city','dateandtime'],how='left').drop('dateandtime',axis=1)


datac['coldwarm'] = datac.temperature_2m.apply(lambda x: 'cold' if x<10 else 'warm')
datac['rainydry'] = datac.rain.apply(lambda x: 'rainy' if x>1 else 'dry')

datac['temp_cat'] = pd.qcut(datac.temperature_2m,q=[0,0.2,0.4,0.6,0.8,1],labels=['freezing','cold','comfortable','warm','hot'])

    
datac.head()
datac.tail()



#%% plot the amount of trafic per month
datac.sort_values(by='month').groupby('month',observed=True).Duration.count().plot(kind='bar')
plt.title('Number of trafics per month')
plt.ylabel('counts')
plt.show()

#%% plot the amount of trafic per weekday split per am/pm
datac.sort_values(by='weekday').groupby(['weekday','ampm'],observed=True).Duration.count().unstack('ampm').plot(kind='bar')
plt.title('Number of trafics per weekday')
plt.ylabel('counts')
plt.show()

#%% plot the amount of trafic per road
plt.figure(figsize=(20,12))
# plt.subplot(1,2,1)
plt_data = datac.query('Road.str.contains("A")').groupby(['Road'],observed=True)
plt_data['Duration'].count().sort_values(ascending=False).plot.bar(figsize=(12,6))
plt.title('Number of trafics per road')
plt.ylabel('counts')
plt.show()

# datac["group_based_max"] = plt_data.HPstart.transform('max')
# plt.subplot(1,2,2)
# datac.query('Road.str.contains("A")').groupby(['Road'],observed=True)['Duration'].count()/(datac['group_based_max']).plot.bar(figsize=(12,6))
# plt.title('Number of trafics per road')
# plt.ylabel('counts')
# plt.show()

#%% plot the amount of trafic per road splitted per am/pm
datac.query('Road.str.contains("A")').groupby(['Road','ampm'],observed=True)['Duration'].count().unstack('ampm').sort_values(by=['pm','am'],ascending=False).plot.bar(figsize=(12,6))
plt.title('Number of trafics per road splitted per am/pm')
plt.ylabel('counts')
plt.show()

#%% plot the amount of trafic per HP for a specific road splitted per am/pm
road = 'A27'
nbins = 100
gbo_per_road = datac.query('Road.str.contains("A")').groupby(['Road'],observed=True)
gbo_per_road.get_group(road)
am_oplopend = gbo_per_road.get_group(road).query('ampm=="am" & direction=="oplopend"').explode('HPrange')
pm_oplopend = gbo_per_road.get_group(road).query('ampm=="pm" & direction=="oplopend"').explode('HPrange')
am_aflopend = gbo_per_road.get_group(road).query('ampm=="am" & direction=="aflopend"').explode('HPrange')
pm_aflopend = gbo_per_road.get_group(road).query('ampm=="pm" & direction=="aflopend"').explode('HPrange')

plt.figure(figsize=(20,12))
plt.suptitle(('{}').format(road))
plt.subplot(2,2,1)
plt.hist([am_oplopend.query('Duration<@shortlong_border')['HPrange'],pm_oplopend.query('shortlong=="short"')['HPrange']],bins=nbins,label=['am','pm'])
plt.title('# of SHORT trafics splitted per am/pm - Oplopend')
plt.ylabel('counts')
plt.xlabel('Hectometer paal')
plt.legend()

plt.subplot(2,2,2)
plt.hist([am_aflopend.query('Duration<@shortlong_border')['HPrange'],pm_aflopend.query('shortlong=="short"')['HPrange']],bins=nbins,label=['am','pm'])
plt.title('# of SHORT trafics splitted per am/pm - Aflopend')
plt.ylabel('counts')
plt.xlabel('Hectometer paal')
plt.legend()

plt.subplot(2,2,3)
plt.hist([am_oplopend.query('Duration>@shortlong_border')['HPrange'],pm_oplopend.query('shortlong=="long"')['HPrange']],bins=nbins,label=['am','pm'])
plt.title('# of LONG trafics splitted per am/pm - Oplopend')
plt.ylabel('counts')
plt.xlabel('Hectometer paal')
plt.legend()

plt.subplot(2,2,4)
plt.hist([am_aflopend.query('Duration>@shortlong_border')['HPrange'],pm_aflopend.query('shortlong=="long"')['HPrange']],bins=nbins,label=['am','pm'])
plt.title('# of LONG trafics splitted per am/pm - Aflopend')
plt.ylabel('counts')
plt.xlabel('Hectometer paal')
plt.legend()

plt.show()
#plt.savefig(r"C:\Users\rbijman\Documents\GitHub\rgbijmanproductions\ALTEN\Files\Output\Plots\test.png")

#%%
plt.figure(figsize=(20,12))
plt_data = datac.query('Road.str.contains("A12") & Duration>50')
sns.stripplot(data=plt_data,y='Road',x='Duration',hue='month',dodge=True)
plt.xticks(rotation=90)
plt.show()

#%% plot per day per road number of files
road = 'A12'
gbo_per_road = datac.groupby(['Road'],observed=True)
hp=39.1
plt_data = gbo_per_road.get_group(road).explode('HPrange')
plt.hist([plt_data.query('HPrange==@hp & direction=="aflopend"').date,plt_data.query('HPrange==@hp & direction=="oplopend"').date],bins=365)
plt.xticks(plt_data.date.sort_values().unique()[::10],rotation=90)
plt.show()

#%%
max_counts = []
max_hp = []
for road in datac.Road.unique():
    max_counts.append(datac.query('Road==@road').explode('HPrange').HPrange.value_counts().iloc[0])
    max_hp.append(datac.query('Road==@road').explode('HPrange').HPrange.value_counts().index[0])
    
pd.DataFrame(list(zip(datac.Road.unique(),max_hp,max_counts)))



#%% Some statistics
agg_func = 'mean'
column_of_interest = 'distance_rel' #Duration

op_vs_af = pd.crosstab(datac.Road,datac.direction,datac[column_of_interest],aggfunc=agg_func,dropna=True).fillna(pd.NA)  
short_vs_long = pd.crosstab(datac.Road,datac.shortlong,datac[column_of_interest],aggfunc=agg_func).fillna(pd.NA)  
am_vs_pm = pd.crosstab(datac.Road,datac.ampm,datac[column_of_interest],aggfunc=agg_func).fillna(pd.NA)   
per_weekday = pd.crosstab(datac.Road,datac.weekday.sort_values().map(day_map),datac[column_of_interest],aggfunc=agg_func)[['Mon','Thu','Wed','Thu','Fri','Sat','Sun']].fillna(pd.NA)  
per_month = pd.crosstab(datac.Road,datac.month.sort_values().map(month_map),datac[column_of_interest],aggfunc=agg_func).fillna(pd.NA)  
cold_vs_warm = pd.crosstab(datac.Road,datac.coldwarm,datac[column_of_interest],aggfunc=agg_func).fillna(pd.NA)
rainy_vs_dry = pd.crosstab(datac.Road,datac.rainydry,datac[column_of_interest],aggfunc=agg_func).fillna(pd.NA)
temp_cat = pd.crosstab(datac.Road,datac.temp_cat,datac[column_of_interest],aggfunc=agg_func).fillna(pd.NA)


trafic_per_cat = pd.concat([op_vs_af,short_vs_long,am_vs_pm,per_weekday,per_month,temp_cat,rainy_vs_dry],axis=1)
trafic_per_cat['Total'] = datac.groupby('Road')[column_of_interest].agg(agg_func)

trafic_per_cat_ranked= trafic_per_cat.rank(ascending=False,method='max').sort_values(by='Total')

plt.figure(figsize=(20,20))
sns.heatmap(trafic_per_cat_ranked,cmap='RdYlGn_r',annot=True,fmt='2.0f',cbar_kws={'label': 'Ranks'})
plt.title(('Ranked acorrding to {} {} per category and sorted by Total').format(agg_func,column_of_interest))
plt.show()


# CHECK https://services.arcgis.com/nSZVuSZjHpEZZbRo/ArcGIS/rest/services/NWB_Hectometerpaaltjes/FeatureServer/0/queryTopFeatures?where=A12&topFilter=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&outFields=&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&outSR=&defaultSR=&returnIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&cacheHint=false&collation=&orderByFields=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnTrueCurves=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=html&token=


#%%
datac.groupby(by='month').temperature.mean().div(datac.temperature.max()).plot()
datac.groupby(by='month').Duration.count().div(datac.Duration.count()).plot()
plt.show()


sns.jointplot(datac,x='Duration',y='temperature')
plt.show()

sns.jointplot(datac,x='temperature',y='rain')
plt.show()


#%%
datac.groupby(by='trajectA').temp.mean()
plt.show()

#%%
plt.bar(x=datac.query("rainydry=='dry'").Road.sort_values().unique(),height=datac.query("rainydry=='dry'").groupby(by='Road').Duration.mean(),label='dry',color='red',alpha=.3)
plt.bar(x=datac.query("rainydry=='rainy'").Road.sort_values().unique(),height=datac.query("rainydry=='rainy'").groupby(by='Road').Duration.mean(),label='rainy',color='green',alpha=.3)
plt.xticks(rotation=90)
plt.ylabel('Duration')
plt.title('Mean Duration of trafics per road splitted by rainy/dry conditions')
plt.legend()
plt.show()

#%%

datac.groupby(by=['lat','lon']).Duration.mean().reset_index().plot.scatter('lon','lat',c='Duration')
plt.show()

datac.groupby(by=['lat','lon']).temperature_2m.min().reset_index().plot.scatter('lon','lat',c= 'temperature_2m')
plt.show()


plt.scatter(datac.lon,datac.lat,datac.Duration/10)
plt.xlabel('lon')
plt.xlabel('lat')


cities_of_interest = ['Utrecht','Amsterdam','Rotterdam','Eindhoven','Zwolle']

test = lat_lon_df.query("city in @cities_of_interest")

for idx,city in enumerate(test.city):
    plt.annotate(test.city.iloc[idx], (test.lon.iloc[idx],test.lat.iloc[idx]))

plt.show()

#%% 
agg_type = 'min'
temperature_per_city.query("lat>50 & lon>0 & lon<8").groupby('city').agg({'lon':agg_type,'lat':agg_type,'temperature_2m':agg_type}).plot.scatter(x='lon',y='lat',c='temperature_2m')
plt.title(('{} temperature per city').format(agg_type))
plt.show()
