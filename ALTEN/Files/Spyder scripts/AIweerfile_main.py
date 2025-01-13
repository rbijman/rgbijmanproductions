# -*- coding: utf-8 -*-

#%% import
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

#%% Variable defitions
shortlong_border = 20
ampm_border = 12

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
datac['Road'] = data.RouteOms.astype('category')
datac['HPstart'] = data.HectometerKop.str.replace(',','.').astype('float64')
datac['HPend'] = data.HectometerStaart.str.replace(',','.').astype('float64')
datac['direction'] = data.hectometreringsrichting;
datac['HPrange'] = datac.apply(lambda x: getHPrange(x['HPstart'],x['HPend']),axis=1)
datac['ampm'] = datac.DateTimeStart.dt.time.apply(lambda x: 'am' if x<datetime.time(ampm_border) else 'pm')
datac['shortlong'] = datac.Duration.apply(lambda x: 'short' if x<shortlong_border else 'long')
datac['month'] = data.DatumFileBegin.apply(lambda x: x[5:7]).astype(int)
datac

#%% plot the amount of trafic per month
datac.groupby('month',observed=True).Duration.count().plot(kind='bar')
plt.title('Number of trafics per month')
plt.ylabel('counts')
plt.show()

#%% plot the amount of trafic per road splitted per am/pm
gbo_per_road = datac.query('Road.str.contains("A")').groupby(['Road','ampm'],observed=True)['Duration'].count().unstack('ampm').plot.bar(figsize=(12,6))
plt.title('Number of trafics per road splitted per am/pm')
plt.ylabel('counts')
plt.show()
