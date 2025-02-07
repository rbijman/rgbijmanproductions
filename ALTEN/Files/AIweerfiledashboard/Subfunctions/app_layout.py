# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 13:50:23 2025

@author: rbijman
"""

def main(app,dcc,html,datac,data):
    
    app.layout = html.Div(
        children=[
            
            dcc.Tabs([
                dcc.Tab(id='trafic',label='Trafic',children=[
                    
                    html.H1(children="Trafic Analytics"),
                    html.P(
                        children=(
                            "Analyze all Trafics"
                        ),
                    ),
                    html.Div(["Select a month: "]),
    
                    dcc.RadioItems(datac.index.month.unique(), 1,id='month_select_trafic',inline=True),
                    
                    dcc.DatePickerRange(
                    id='date_range_trafic',
                    min_date_allowed=datac.index.round('D').min(),
                    max_date_allowed=datac.index.round('D').max(),
                    initial_visible_month=datac.index.min(),
                    start_date=datac.index.min(),
                    end_date=datac.index.max()
                    ),
                    
                    
                    html.Div(["Select Road: "]),
                    dcc.Dropdown(datac.Road.sort_values().unique(),'A1',id='road_select_trafic'),
                    
                    html.Div(["Split by: "]),
    
                    dcc.RadioItems(['no_split','direction','ampm','shortlong','weekday'], 'no_split',id='split_by_trafic',inline=True),
    
                    html.Div(["Graph1: "]),
                    
                    dcc.Loading(
                    id='loading_trafic1',   
                    children=[
                     dcc.Graph(id="graph_trafic1"),   
                        ]
                    ),
                    
                    html.Div(["Graph2: "]),

                    
                    dcc.Loading(
                    id='loading_trafic2',   
                    children=[
                      dcc.Graph(id="graph_trafic2"),   
                        ]
                    ),
                    
                    ]),
                
                dcc.Tab(id='weather_and_trafic',label='Weather+Trafic',children=[
                    html.H1(children="Weather + Trafic Analytics"),
                    html.P(
                        children=(
                            "Analyze weather + trafic"
                        ),
                    ),
                    html.Div(["Select a month: "]),
    
                    dcc.RadioItems(datac.index.month.unique(), 1,id='month_select_weather',inline=True),
                    
                    dcc.DatePickerRange(
                    id='date_range_weather',
                    min_date_allowed=datac.index.round('D').min(),
                    max_date_allowed=datac.index.round('D').max(),
                    initial_visible_month=datac.index.min(),
                    start_date=datac.index.min(),
                    end_date=datac.index.max()
                    ),
                    
                    
                    html.Div(["Select City: "]),
                    dcc.Dropdown(data.city.sort_values().unique(),'Gouda',id='city_select'),
                    html.Div(["Select Road: "]),
                    dcc.Dropdown(datac.Road.sort_values().unique(),'A1',id='road_select_weather'),
                    
                    html.Div(["Split by: "]),    
                    dcc.RadioItems(['no_split','direction','ampm','shortlong','weekday'], 'no_split',id='split_by_weather',inline=True),
                    
                    html.Div(["Weather type: "]),
    
                    dcc.RadioItems(['temperature_2m','rain'], 'temperature_2m',id='weather_type',inline=True),
    
                    
                    dcc.Loading(
                    id='loading_weather',   
                    children=[
                      dcc.Graph(id="graph_weather"),   
                        ]
                    ),
                    
                    
                    
                    ]),
                
                ])
            
    
            
        ]
    )
    return app
