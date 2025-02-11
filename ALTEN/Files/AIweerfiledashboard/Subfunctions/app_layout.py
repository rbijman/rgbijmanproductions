# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 13:50:23 2025

@author: rbijman
"""

def main(app,dcc,html,datac,data):
    
    app.layout = html.Div(
        children=[
            
            dcc.Tabs(value='further',children=[
                trafic_tab(dcc,html,datac),
                weather_tab(dcc,html,data,datac),
                further_tab(dcc,html,data,datac)
                ])  
        ]
    )
    return app


def trafic_tab(dcc,html,datac):
    tab_name = 'trafic'
    trafic_tab = dcc.Tab(id=tab_name,value=tab_name,label='Trafic',children=[
    
    html.H1(children="Trafic Analytics"),
    html.P(
        children=(
            "Analyze all Trafics"
        ),
    ),
 
    html.Div(["Select a month: "]),
    __month_picker(dcc,datac,tab_name),    
    html.Div(["Or select a specific date range: "]),
    __date_picker(dcc,datac,tab_name),    

    html.Div(["Select road: "]),
    __road_picker(dcc, datac, tab_name),
    
    html.Div(["Split by: "]),
    __split_by_picker(dcc,tab_name),

    html.Div(["Graph1: "]),
    
    dcc.Loading(
    id='loading_trafic1',   
    children=[
     dcc.Graph(id=("graph_{}1").format(tab_name)),   
        ]
    ),
    
    html.Div(["Graph2: "]),
    
    dcc.Loading(
    id='loading_trafic2',   
    children=[
      dcc.Graph(id=("graph_{}2").format(tab_name)),   
        ]
    ),
    
    ])
    return trafic_tab

def weather_tab(dcc,html,data,datac):
    tab_name = 'weather_and_trafic'
    weather_tab = dcc.Tab(id=tab_name,value=tab_name,label='Weather+Trafic',children=[
        html.H1(children="Weather + Trafic Analytics"),
        html.P(
            children=(
                "Analyze weather + trafic"
            ),
        ),

         html.Div(["Select a month: "]),
        __month_picker(dcc,datac,tab_name),            
        html.Div(["Or select a specific date range: "]),
        __date_picker(dcc,datac,tab_name),            
                
        html.Div(["Select road: "]),
        __road_picker(dcc, datac, tab_name),           
        html.Div(["Select city: "]),
        __city_picker(dcc,data,tab_name),        
        
        html.Div(["Split by: "]),    
        __split_by_picker(dcc,tab_name),
        
        html.Div(["Select weather type: "]),
        __weather_type_picker(dcc, data, tab_name),

        dcc.Loading(
        id='loading_weather',   
        children=[
          dcc.Graph(id=("graph_{}").format(tab_name)),   
            ]
        ),
        
        ])
    return weather_tab

def further_tab(dcc,html,data,datac):
    tab_name = 'further'
    new_tab = dcc.Tab(id=tab_name,value=tab_name,label='further',children=[
        html.H1(children="further"),
        html.P(
            children=(
                "Further analyses"
            ),
        ),
        html.Div(["Select a month: "]),
        __month_picker(dcc,datac,tab_name),             
        html.Div(["Or select a specific date range: "]),
        __date_picker(dcc,datac,tab_name),             
    
        html.Div(["Select road: "]),
        __road_picker(dcc, datac, tab_name),             
        html.Div(["Select city: "]),
        __city_picker(dcc,data,tab_name), 
                  
         html.Div(["Select weather type: "]),
         __weather_type_picker(dcc, data, tab_name),
         
         html.Div(["Select trafic information: "]),
         __trafic_information_picker(dcc,tab_name),
         
         html.Div(["Select statistic: "]),
         __statistic_picker(dcc,tab_name),
         
          html.Div(["Select frequency: "]),
          __frequence_picker(dcc,tab_name),
         
         html.Div(["Select weekdays of interest: "]),
         __weekday_picker(dcc,tab_name),

        html.Div(["Select rootcause: "]),
        __rootcause_picker(dcc,datac,tab_name),

        
        dcc.Loading(
        id='loading_further',   
        children=[
          dcc.Graph(id="graph_further"),   
            ]
        ),
        
        ])
    return new_tab


def __month_picker(dcc,datac,tab_name):
    return dcc.Dropdown(datac.index.month.unique(), 1,id=('month_select_{}').format(tab_name),style={'width': '20%'})

def __date_picker(dcc,datac,tab_name):
    return dcc.DatePickerRange(
    id=('date_range_{}').format(tab_name),
    min_date_allowed=datac.index.round('D').min(),
    max_date_allowed=datac.index.round('D').max(),
    initial_visible_month=datac.index.min(),
    start_date=datac.index.min(),
    end_date=datac.index.max(),style={'Height':10}
    )
    
def __road_picker(dcc,datac,tab_name):
    return dcc.Dropdown(datac.Road.sort_values().unique(),'A1',id=('road_select_{}').format(tab_name),style={'width': '25%'})
    
def __split_by_picker(dcc,tab_name):
    return dcc.RadioItems(['no_split','direction','ampm','shortlong','weekday'], 'no_split',id=('split_by_{}').format(tab_name),inline=True)
    
def __city_picker(dcc,data,tab_name):
    return dcc.Dropdown(data.city.sort_values().unique(),placeholder='Select another city',id=('city_select_{}').format(tab_name),style={'width': '50%'})
    
def __weather_type_picker(dcc,data,tab_name):
    return dcc.RadioItems(options={'temperature_2m':'temperature','rain':'rain'},value= 'temperature_2m',id=('weather_type_{}').format(tab_name),inline=True)

def __trafic_information_picker(dcc,tab_name):
    return dcc.RadioItems(options={'Duration':'duration','distance':'distance'},value='Duration',id=('trafic_information_{}').format(tab_name),inline=True)

def __statistic_picker(dcc,tab_name):
    return dcc.RadioItems(['mean','max','min','count'],'mean',id=('statistic_{}').format(tab_name),inline=True)

def __weekday_picker(dcc,tab_name):
    return dcc.Checklist(['0','1','2','3','4','5','6','all'],['1'],id=('weekday_{}').format(tab_name),inline=True)

def __frequence_picker(dcc,tab_name):
    return dcc.RadioItems(options={'ME':'month','D':'day','h':'hour'},value='D',id=('frequency_{}').format(tab_name),inline=True)

def __rootcause_picker(dcc,datac,tab_name):
    return dcc.Checklist(datac.Oorzaak_4.unique(),datac.Oorzaak_4.unique().tolist(),id=('rootcause_{}').format(tab_name),inline=True)