# -*- coding: utf-8 -*-

#%% import
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

#%% Variable defitions
shortlong_border = 20
ampm_border = 12
month_map = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
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
datac['direction'] = data.hectometreringsrichting;
datac['HPrange'] = datac.apply(lambda x: getHPrange(x['HPstart'],x['HPend']),axis=1)
datac['ampm'] = datac.DateTimeStart.dt.time.apply(lambda x: 'am' if x<datetime.time(ampm_border) else 'pm')
datac['shortlong'] = datac.Duration.apply(lambda x: 'short' if x<shortlong_border else 'long')
datac['month'] = data.DatumFileBegin.apply(lambda x: x[5:7]).astype(int).astype('category')
datac['date'] = datac.DateTimeStart.dt.date
datac['season'] = pd.cut(datac.month,season_bins,right=True,labels=season_names)
datac['weekday'] = datac.DateTimeStart.dt.dayofweek
datac.head()
datac.tail()


#JOIN WEATHER DATA

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