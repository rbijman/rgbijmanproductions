# -*- coding: utf-8 -*-

#%% import
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import sys
sys.path.insert(0,r'C:\Users\rbijman\Documents\GitHub\rgbijmanproductions\ALTEN\Files\AIweerfiledashboard\Subfunctions')
import AIweerfile_functions

#%% Variable defitions
shortlong_border = 20
ampm_border = 12
start_date = '2024-01-01'
end_date = '2024-12-31'

datac, lat_lon_df, weather_per_city = AIweerfile_functions.collect_and_clean_AIweerfiledata(start_date,end_date,ampm_border,shortlong_border)





#%% plot the amount of trafic per month
datac.sort_values(by='date').groupby('month',observed=True).Duration.count().plot(kind='bar')
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
column_of_interest = 'distance' #Duration

op_vs_af = pd.crosstab(datac.Road,datac.direction,datac[column_of_interest],aggfunc=agg_func,dropna=True).fillna(pd.NA)  
short_vs_long = pd.crosstab(datac.Road,datac.shortlong,datac[column_of_interest],aggfunc=agg_func).fillna(pd.NA)  
am_vs_pm = pd.crosstab(datac.Road,datac.ampm,datac[column_of_interest],aggfunc=agg_func).fillna(pd.NA)   
per_weekday = pd.crosstab(datac.Road,datac.DateTimeStart.sort_values().dt.day_name().apply(lambda x:x[0:3]),datac[column_of_interest],aggfunc=agg_func)[['Mon','Thu','Wed','Thu','Fri','Sat','Sun']].fillna(pd.NA)  
per_month = pd.crosstab(datac.Road,datac.DateTimeStart.sort_values().dt.month_name().apply(lambda x: x[0:3]),datac[column_of_interest],aggfunc=agg_func).fillna(pd.NA)  
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
datac.groupby(by='month').temperature_2m.mean().div(datac.temperature_2m.max()).plot()
datac.groupby(by='month').Duration.count().div(datac.Duration.count()).plot()
plt.show()


# sns.jointplot(datac,x='Duration',y='temperature_2m')
# plt.show()

# sns.jointplot(datac,x='temperature_2m',y='rain')
# plt.show()


#%%
plt.bar(x=datac.query("rainydry=='dry'").Road.sort_values().unique(),height=datac.query("rainydry=='dry'").groupby(by='Road').Duration.mean(),label='dry',color='red',alpha=.3)
plt.bar(x=datac.query("rainydry=='rainy'").Road.sort_values().unique(),height=datac.query("rainydry=='rainy'").groupby(by='Road').Duration.mean(),label='rainy',color='green',alpha=.3)
plt.xticks(rotation=90)
plt.ylabel('Duration')
plt.title('Mean Duration of trafics per road splitted by rainy/dry conditions')
plt.legend()
plt.show()

#%%
datac = pd.merge(left=datac,right=lat_lon_df,left_on='trajectA',right_on='city',suffixes=['_city','_A'],how='left').rename(columns={"city_city":"city",'lat_city':'lat','lon_city':'lon'}).drop(columns="city_A")
datac = pd.merge(left=datac,right=lat_lon_df,left_on='trajectB',right_on='city',suffixes=['_city','_B'],how='left').rename(columns={"city_city":"city"}).drop(columns="city_B")
datac['lat_middle'] = datac[['lat_A','lat_B']].mean(axis=1)
datac['lon_middle'] = datac[['lon_A','lon_B']].mean(axis=1)

fig, gax = plt.subplots(figsize=(10,10))
url1 = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
world = gpd.read_file(url1)[['SOV_A3', 'POP_EST', 'CONTINENT', 'NAME', 'GDP_MD', 'geometry']]
world = world.set_index("SOV_A3")
world.query('SOV_A3=="NL1"').plot(alpha=0.5,ax=gax)
datac.query('Road=="A4"').groupby(by=['lat_middle','lon_middle']).Duration.mean().reset_index().plot.scatter('lon_middle','lat_middle',c='Duration',cmap='viridis',ax=gax)
cities_of_interest = ['Utrecht','Amsterdam','Rotterdam','Gouda','Eindhoven','Zwolle','Groningen','Maastricht']

test = lat_lon_df.query("city in @cities_of_interest")

for idx,city in enumerate(test.city):
    plt.annotate(test.city.iloc[idx], (test.lon.iloc[idx],test.lat.iloc[idx]))
plt.show()

datac.groupby(by=['lat_middle','lon_middle']).temperature_2m.min().reset_index().plot.scatter('lon_middle','lat_middle',c= 'temperature_2m')
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


agg_type = 'mean'
weather_per_city.query("lat>50 & lon>0 & lon<8").groupby('city').agg({'lon':agg_type,'lat':agg_type,'temperature_2m':agg_type}).plot.scatter(x='lon',y='lat',c='temperature_2m')
plt.title(('{} temperature per city').format(agg_type))
plt.show()


#%%
query = "index.dt.hour.isin([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]) & index.dt.weekday.astype('str').isin(['0','1','2','3','4','5','6']) & Oorzaak_4.isin(['Incident', 'Ongeval', 'Hoge intensiteit', 'Ongepland onderhoud', 'Overige oorzaken', 'Aanleg en gepland onderhoud', '(Zeer extreme) weersomstandigheden', 'Evenement', None]) & Road in ['A10', 'A4', 'A27', 'A58', 'A2', 'N35', 'A1', 'A7', 'N99', 'N9', 'A16', 'A9', 'A12', 'A73', 'N3', 'A67', 'A76', 'A29', 'N57', 'A20', 'N59', 'A50', 'A5', 'N33', 'A15', 'A35', 'A28', 'A8', 'N325', 'A79', 'N50', 'N44', 'A59', 'A325', 'N2', 'A13', 'N61', 'N36', 'A18', 'N7', 'A348', 'N11', 'A270', 'A44', 'A30', 'A22', 'N65', 'A6', 'N200', 'N256', 'A32', 'A208', 'N348', 'N48', 'A17', 'N18', 'N31', 'A38', 'A65', 'A326', 'A200', 'N46', 'N15', 'A77', 'N326', 'N270', 'A74', 'N209', 'A256', 'A37', 'A31', 'N14', 'N343', 'N307', 'N370', 'N32', 'N434', 'N230']"

weathertype = 'wind_speed_10m'

plt.scatter(x=datac.query(query).reset_index().resample('D',on='DateTimeStart')[weathertype].max(),y=datac.query(query).reset_index().resample('D',on='DateTimeStart')['GemLengte'].count())
plt.show()

from scipy.stats import spearmanr

df = pd.DataFrame()
df['pres'] = datac.query(query).reset_index().resample('D',on='DateTimeStart')[weathertype].max()
df['leng'] = datac.query(query).reset_index().resample('D',on='DateTimeStart')['GemLengte'].count()
spearmanr(df.dropna().pres,df.dropna().leng)
