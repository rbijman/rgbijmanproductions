# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 13:05:19 2025

@author: rbijman
"""

#%%

#run in anaconda prompt: python Documents\GitHub\rgbijmanproductions\ALTEN\Files\AIweerfiledashboard\AIweerfiledashboard.py
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback

from Subfunctions import app_layout, callbacks

data = pd.read_pickle(r"C:\Users\rbijman\Documents\GitHub\rgbijmanproductions\ALTEN\Files\weather_data")
data = data.set_index('dateandtime')
datac = pd.read_pickle(r"C:\Users\rbijman\Documents\GitHub\rgbijmanproductions\ALTEN\Files\datac")
datac = datac.sort_values(by=['DateTimeStart','weekday']).set_index('DateTimeStart')

app = Dash(__name__)

app = app_layout.main(app, dcc, html, datac,data)

callbacks.trafic(callback,Output,Input,pd,px,datac)

callbacks.weather(callback,Output,Input,pd,px,data,datac)

callbacks.further(callback, Output, Input, pd, px, data, datac)

if __name__ == "__main__":
    app.run_server(debug=True)