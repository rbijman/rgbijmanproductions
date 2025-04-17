# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 13:05:19 2025

@author: rbijman

"""

# Folderstructure needed:
    
# ..\AIWeerfiledashboard\
# 	AIweerfiledashboard.py
#   	Subfunctions\
#       __initi__.py
# 		app_layout.py
# 		callbacks.py
# 		AIweerfile_functions.py
# ..\API\
# 		api_to_sql_database.py
# 		api_utils.py
# ..\SQL\
# 	python_posgress_class.py
# ..\ProcessedData\
# 	datac
# 	weather_data
# ..\database_config.ini

#start API in anaconda prompt: python Documents\GitHub\rgbijmanproductions\ALTEN\Files\AIweerfiledashboard\api\api_to_sql_database.py
#run in anaconda prompt: python Documents\GitHub\rgbijmanproductions\ALTEN\Files\AIweerfiledashboard\AIweerfiledashboard.py

#%%

import pandas as pd
from dash import Dash
import dash_bootstrap_components as dbc
from Subfunctions import app_layout, callbacks
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
    traffic_data = pd.read_pickle(working_dir + r"\ProcessedData\datac")
    traffic_data = traffic_data.sort_values(by=['DateTimeStart','weekday']).set_index('DateTimeStart')
    print('ready loading the data')
else:
    traffic_data = None
    weather_data = None

app = Dash(__name__,external_stylesheets=[dbc.themes.CERULEAN])

app = app_layout.main(app,api_base)
callbacks.main(weather_data,traffic_data,working_dir,api_base)

if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)