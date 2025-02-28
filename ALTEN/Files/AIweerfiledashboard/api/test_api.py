# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 16:22:30 2025

@author: rbijman
"""

import requests
import pandas as pd

base = 'http://127.0.0.1:5000/'

response = requests.get(base + 'AIWeerFile_api/main?table=trafics&columns="Road","direction"&"Road"=A12,A1')
data = response.json()
df = pd.DataFrame(data['data'],columns=data['columns'])
print(df.head())
print(df.shape)

# response = requests.get(base + 'AIWeerFile_api?table=trafics&columns="Road","direction"&filters="Road"=A12')
# data = response.json()
# df = pd.DataFrame(data['data'],columns=data['columns'])
# print(df.head())
# print(df.shape)

response = requests.get(base + 'AIWeerFile_api/main?table=trafics&columns="Road",direction,"DateTimeStart"&"Road"=A12&start_date=2024-01-01&end_date=2024-01-31&hours=7,8,9&weekdays=1,2,3')
data = response.json()
df = pd.DataFrame(data['data'],columns=data['columns'])
print(df.head())
print(df.shape)


response = requests.get(base + 'AIWeerFile_api/unique?columns="Road"')
data = response.json()
print(data)

response = requests.get(base + 'AIWeerFile_api/unique?columns=month')
data = response.json()
print(data)