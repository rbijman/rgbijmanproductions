# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 13:05:19 2025

@author: rbijman

"""

# Folderstructure needed:
    
#     \working_dir\
#         - AIweerfiledashboard
#         - ProcessedData
#         - RawData
#         - SQL


#%%

#start API in anaconda prompt: python Documents\GitHub\rgbijmanproductions\ALTEN\Files\AIweerfiledashboard\api\
#run in anaconda prompt: python Documents\GitHub\rgbijmanproductions\ALTEN\Files\AIweerfiledashboard\AIweerfiledashboard.py
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State, callback, callback_context
import dash_bootstrap_components as dbc
from Subfunctions import app_layout, callbacks, AIweerfile_functions
import sys

if len(sys.argv)==1:
    use_pickle=0
else:
    use_pickle = int(sys.argv[1])

print(use_pickle)

working_dir = r"C:\Users\rbijman\Documents\GitHub\rgbijmanproductions\ALTEN\Files"
api_base = 'http://127.0.0.1:5000/AIWeerFile_api/'

if use_pickle==1:
    print('loading the data')
    weather_data = pd.read_pickle(working_dir + r"\ProcessedData\weather_data")
    weather_data = weather_data.sort_values(by='date').set_index('date')
    datac = pd.read_pickle(working_dir + r"\ProcessedData\datac")
    datac = datac.sort_values(by=['DateTimeStart','weekday']).set_index('DateTimeStart')
    print('ready loading the data')
else:
    datac = None
    weather_data = None

app = Dash(__name__,external_stylesheets=[dbc.themes.CERULEAN])

app = app_layout.main(app, dcc, dbc, html, datac,weather_data,pd, api_base,AIweerfile_functions)
callbacks.main(callback, Output, Input, State, pd, px, weather_data,datac,working_dir,api_base,AIweerfile_functions,callback_context)

if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)