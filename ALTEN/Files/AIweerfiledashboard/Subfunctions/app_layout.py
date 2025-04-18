# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 13:50:23 2025

@author: rbijman
"""


# class python_postgres:

#     def __init__(self,app,weather_data,api_base):
#         self.api_base = api_base
        
#         app.layout = html.Div(children=[            
#                 dcc.Tabs(value='further',children=[
#                     update_data_tab(self),
#                     AIWeerFile_tab(self),
#                     ])  
#             ])
#         return app
                
import pandas as pd
from dash import dcc, html
import dash_bootstrap_components as dbc


def main(app,api_base):
    app.layout = html.Div(children=[             
            dcc.Tabs(value='further',children=[  #further
                AIWeerFile_tab(api_base),
                update_data_tab(),
                traffic_tab(api_base),
                weather_tab(api_base),
                # heatmap_tab(),                
            ])  
    ])
    return app

def update_data_tab():
    tab_name = 'update_data'
    update_data_tab = dcc.Tab(id=tab_name,value=tab_name,label='Update data',children=[
    
        html.H1(children="Update data"),
            dbc.Stack([
                dbc.Row([
                    dbc.Col([
                        html.Div(["Select a specific date range: "]),
                        dcc.DatePickerRange(id=('date_range_{}').format(tab_name),min_date_allowed='2000-01-01',max_date_allowed=str(pd.Timestamp.now().date()),initial_visible_month='2024-01-01',start_date='2024-01-01',end_date='2024-12-31')
                    ],width=2),
                    dbc.Col([
                        html.Div(["Define shortlong_border: "]),
                        html.Div([dcc.Input(id='input_shortlong_border', type='number',value=20)])
                    ],width=1),
                    dbc.Col([
                        html.Div(["Define ampm_border: "]),
                        html.Div([dcc.Input(id='input_ampm_border', type='number',value=12)])
                    ],width=1)
                ]),
                        dbc.Row([
                            dbc.Col([
                                html.Div(html.Button('Update traffic SQL', id='update_traffic_sql_button', n_clicks=0),),
                                ],width=1),
                            dbc.Col([
                                html.Div(html.Button('Update weather SQL', id='update_weather_sql_button', n_clicks=0),)
                                ],width=1),
                            dbc.Col([
                                    html.Div(html.Button('Update pickle', id='update_pickle_button', n_clicks=0))
                            ],width=1),
                        ]),
                
                    html.Div(dcc.Textarea(id=('loading_status_{}').format(tab_name)))
            ],gap=2)
    ])        

    return update_data_tab

def traffic_tab(api_base):
    tab_name = 'traffic'
    trafic_tab = dcc.Tab(id=tab_name,value=tab_name,label='Traffic',children=[
    
    html.H1(children="Traffic Analytics"),
  
    
    dbc.Stack([
        dbc.Stack([
            html.Div(["Select a year:"]),
            dcc.Dropdown(options=[],id=('year_select_{}').format(tab_name),style={'width':'100px'}),
            html.Div(["Select a month: "]),
            dcc.Dropdown(options=[],id=('month_select_{}').format(tab_name),style={'width':'100px'}),       
            html.Div(["Or select a specific date range: "]),
            dcc.DatePickerRange(id=('date_range_{}').format(tab_name))
        ],direction="horizontal",gap=3),
        dbc.Stack([
                           
            html.Div(["Select road try: "]),
            dcc.Dropdown(options=[],id=('road_select_{}').format(tab_name),style={'width':'100px'}), 
           
            html.Div(["Split by: "]),
            __split_by_picker(tab_name),
            
            
        ],direction="horizontal",gap=3),
    ],gap=3),
    
    html.Div(html.Button('Load data', id='load_data_{}'.format(tab_name), n_clicks=0)),

    html.Div(["Graph1: "]),
    dcc.Loading(id='loading_traffic1',children=[
        dcc.Graph(id=("graph_{}1").format(tab_name)),   
    ]),
    
    html.Div(["Graph2: "]),
    dcc.Loading(id='loading_trafic2',children=[
        dcc.Graph(id=("graph_{}2").format(tab_name)),   
    ]),
    
    html.Div(["exclude those traffics: "]),
    dcc.Checklist(['grens','>25km'],[],id=('excluded_traffics_{}').format(tab_name),inline=True),        

    dcc.Store(id='dropdown_options_store_{}'.format(tab_name)),

    ])
    return trafic_tab

def weather_tab(api_base):
    tab_name = 'weather_and_traffic'
    weather_tab = dcc.Tab(id=tab_name,value=tab_name,label='Weather+Traffic',children=[
        html.H1(children="Weather + Traffic Analytics"),
        
        
        dbc.Stack([
            dbc.Stack([
                html.Div(["Select a year:"]),
                dcc.Dropdown(options=[],id=('year_select_{}').format(tab_name),style={'width':'100px'}),
                html.Div(["Select a month: "]),
                dcc.Dropdown(options=[],id=('month_select_{}').format(tab_name),style={'width':'100px'}),       
                html.Div(["Or select a specific date range: "]),
                dcc.DatePickerRange(id=('date_range_{}').format(tab_name))
            ],direction="horizontal",gap=3),
            dbc.Stack([
                               
                html.Div(["Select road try: "]),
                dcc.Dropdown(options=[],id=('road_select_{}').format(tab_name),style={'width':'100px'}), 
                
                html.Div(["Select city: "]),
                dcc.Dropdown(options=[],placeholder='Select another city',id=('city_select_{}').format(tab_name),style={'width':'300px'}),
               
                html.Div(["Split by: "]),
                __split_by_picker(tab_name),
                
            ],direction="horizontal",gap=3),
            dbc.Stack([
                
                html.Div(["Select weather type: "]),
                __weather_type_picker(tab_name),
                
            ],direction="horizontal",gap=3),
        ],gap=3),     
        
        html.Div(html.Button('Load data', id='load_data_{}'.format(tab_name), n_clicks=0)),

        dcc.Loading(id='loading_weather',children=[
        dcc.Graph(id=("graph_{}").format(tab_name))]), 
        
        dcc.Store(id='dropdown_options_store_{}'.format(tab_name)),

      
    ])
    return weather_tab

def AIWeerFile_tab(api_base):
    tab_name = 'further'
    
    new_tab = dcc.Tab(id=tab_name,value=tab_name,label='AIWeerFileDashboard',children=[
        html.H1(children="AIWeerFileDashboard"),
        
        dbc.Stack([
            dbc.Stack([
                html.Div(["Select a year:"]),
                dcc.Dropdown(options=[],id=('year_select_{}').format(tab_name),style={'width':'100px'}),
                html.Div(["Select a month: "]),
                dcc.Dropdown(options=[],id=('month_select_{}').format(tab_name),style={'width':'100px'}),       
                html.Div(["Or select a specific date range: "]),
                dcc.DatePickerRange(id=('date_range_{}').format(tab_name))
            ],direction="horizontal",gap=3),
            dbc.Stack([
                               
                html.Div(["Select road try: "]),
                dcc.Dropdown(options=[],id=('road_select_{}').format(tab_name),style={'width':'100px'}), 
               
                html.Div(["Select city: "]),
                dcc.Dropdown(options=[],placeholder='Select another city',id=('city_select_{}').format(tab_name),style={'width':'300px'})
                
                
                
            ],direction="horizontal",gap=3),
            dbc.Stack([
                html.Div(["Select traffic information: "]),
                __trafic_information_picker(tab_name),
                 
                html.Div(["Select traffic statistic: "]),
                __statistic_picker(tab_name,'traffic'),
                
                html.Div(["Select traffic plot frequency: "]),
                __frequence_picker(tab_name,'traffic'),
                
                html.Div(["Select weather type: "]),
                __weather_type_picker(tab_name),

                html.Div(["Select weather plot frequency: "]),
                __frequence_picker(tab_name,'weather'),
                
                html.Div(["Select weather statistic: "]),
                __statistic_picker(tab_name,'weather'),
                
                html.Div(["Select weather marker size: "]),
                dcc.Dropdown(list(range(8,17,1)),10,id=('weather_marker_size_{}').format(tab_name),style={'width':'100px'})
                
                                
            ],direction="horizontal",gap=3),   

        ],gap=3),
        
        html.Div([dcc.Markdown('''**Apply filters**''')]),
    
        html.Div(["Select weekdays of interest: "]),
        __weekday_picker(tab_name),
        
        html.Div(["Select period on the day of interest: "]),
        __period_picker(tab_name),
         
        html.Div(["Select rootcause: "]),
        dcc.Checklist(options=[],id=('rootcause_{}').format(tab_name),inline=True),

        html.Div(["Number of included trafics"]),
        dcc.Textarea(id=('text_{}').format(tab_name)),
        
        html.Div(["Subtract the per weekday average: "]),
        dcc.Checklist(options=['on'],value=[],id=('subtract_weekday_average_{}').format(tab_name)),
        
        dbc.Row(dbc.Spinner(color="primary", fullscreen=True), id=("initial_spinner_{}").format(tab_name)),

        dcc.Graph(id=("graph_{}").format(tab_name)),   
        
        html.Div(id='graph_field',children=[
            dcc.Loading(
                id=('loading2_{}').format(tab_name),children=[
                    dcc.Graph(id=("graph2_{}").format(tab_name)),   
            ]),
        ]),
        
        html.Div(["Total API query is:"]),
        dcc.Textarea(id=('total_api_query_{}').format(tab_name), style={'width': '25%','height':150}),
        
        html.Div(["Total Pandas query is:"]),
        dcc.Textarea(id=('total_pandas_query_{}').format(tab_name), style={'width': '25%','height':150}),
        
        dcc.Store(id='dropdown_options_store_{}'.format(tab_name)),

        
        ])
    return new_tab

def heatmap_tab():
    tab_name = 'heatmap'
    heatmap_tab = dcc.Tab(id=tab_name,value=tab_name,label='Heatmap',children=[
        html.H1(children="Heatmap"),
        html.P(
            children=(
                "Heatmap"
            ),
        ),
        dcc.Loading(
        id=('loading_{}').format(tab_name),   
        children=[
          dcc.Graph(id=("graph_{}").format(tab_name),style={'width': '90vw', 'height': '90vh'}),   
            ]
        ),
        ])
    return heatmap_tab


#Helper functions
def __split_by_picker(tab_name):
    return dcc.RadioItems(['no_split','direction','ampm','shortlong','weekday'], 'no_split',id=('split_by_{}').format(tab_name),inline=True)

def __weather_type_picker(tab_name):
    return dcc.Dropdown(options={'temperature_2m':'temperature','rain':'rain','snowfall':'snow','precipitation':'precipitation','wind_speed_10m':'wind','sunshine_duration':'sunshine'},value= 'temperature_2m',id=('weather_type_{}').format(tab_name),style={'width':'200px'})

def __trafic_information_picker(tab_name):
    return dcc.Dropdown(options={'Duration':'duration','GemLengte':'distance'},value='Duration',id=('traffic_information_{}').format(tab_name),style={'width':'200px'})

def __statistic_picker(tab_name,suffix):
    return dcc.Dropdown(['mean','max','min','sum','count'],'mean',id=('statistic_{}_{}').format(suffix,tab_name),style={'width':'100px'})

def __weekday_picker(tab_name):
    return dcc.Checklist({'0':'mon','1':'tue','2':'wed','3':'thu','4':'fri','5':'sat','6':'sun','all':'all days'},['1'],id=('weekday_{}').format(tab_name),inline=True)

def __period_picker(tab_name):
    return dcc.Checklist({'0-6':'night_morning','6-10':'morning','10-15':'noon','15-19':'evening','19-24':'night-evening','all':'all day'},['all'],id=('period_{}').format(tab_name),inline=True)

def __frequence_picker(tab_name,suffix):
    return dcc.Dropdown(options={'ME':'month','D':'day','h':'hour'},value='D',id=('frequency_{}_{}').format(suffix,tab_name),style={'width':'100px'})

