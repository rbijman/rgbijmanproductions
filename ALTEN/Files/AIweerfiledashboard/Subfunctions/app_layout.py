# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 13:50:23 2025

@author: rbijman
"""


# class python_postgres:

#     def __init__(self,app,dcc,dbc,html,datac,weather_data,pd,api_base,AIweerfile_functions):
#         self.dcc = dcc
#         self.dbc = dbc
#         self.html = html
#         self.datac = datac
#         self.weather_data = weather_data
#         self.pd = pd
#         self.api_base = api_base
#         self.AIweerFile_functions = AIweerfile_functions
        
#         app.layout = html.Div(children=[            
#                 dcc.Tabs(value='further',children=[
#                     update_data_tab(self),
#                     AIWeerFile_tab(self),
#                     ])  
#             ])
#         return app
                    

def main(app,dcc,dbc,html,datac,weather_data,pd,api_base,AIweerfile_functions):
    app.layout = html.Div(children=[            
            dcc.Tabs(value='further',children=[
                update_data_tab(dcc,html,datac,dbc,pd,AIweerfile_functions),
                AIWeerFile_tab(dcc,html,dbc,pd,weather_data,datac,api_base,AIweerfile_functions),
                # heatmap_tab(dcc,html,datac),
                # traffic_tab(dcc,html,dbc,pd,datac,api_base,AIweerfile_functions),
                # weather_tab(dcc,html,dbc,pd,weather_data,datac,api_base,AIweerfile_functions),
                
            ])  
    ])
    return app

def update_data_tab(dcc,html,datac,dbc,pd,AIweerfile_functions):
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

def traffic_tab(dcc,html,dbc,pd,datac,api_base,AIweerfile_functions):
    tab_name = 'traffic'
    trafic_tab = dcc.Tab(id=tab_name,value=tab_name,label='Traffic',children=[
    
    html.H1(children="Traffic Analytics"),
    dbc.Row([
        dbc.Col([
            html.Div(["Select a year:"]),
            __year_picker(dcc,datac,tab_name,api_base,AIweerfile_functions),
            
            html.Div(["Select a month: "]),
            __month_picker(dcc,datac,tab_name,api_base,AIweerfile_functions),    
        ],width=2),
        dbc.Col([
            html.Div(["Or select a specific date range: "]),
            __date_picker(dcc,pd,datac,tab_name,api_base,AIweerfile_functions),    
        ],width=2),
        dbc.Col([
            html.Div(["Select road: "]),
            __road_picker(dcc, datac, tab_name,'N99',api_base,AIweerfile_functions),
        ],width=2),
        dbc.Col([
            html.Div(["Split by: "]),
            __split_by_picker(dcc,tab_name),
        ],width=2),
    ]), 

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

    
    ])
    return trafic_tab

def weather_tab(dcc,html,dbc,pd,weather_data,datac,api_base,AIweerfile_functions):
    tab_name = 'weather_and_traffic'
    weather_tab = dcc.Tab(id=tab_name,value=tab_name,label='Weather+Traffic',children=[
        html.H1(children="Weather + Traffic Analytics"),
        
        dbc.Row([
            dbc.Col([
                html.Div(["Select a year:"]),
                __year_picker(dcc,datac,tab_name,api_base,AIweerfile_functions),
                
                html.Div(["Select a month: "]),
                __month_picker(dcc,datac,tab_name,api_base,AIweerfile_functions),                   
            ],width=2),
            dbc.Col([
                html.Div(["Or select a specific date range: "]),
                __date_picker(dcc,pd,datac,tab_name,api_base,AIweerfile_functions),   
            ],width=2),
            dbc.Col([
                html.Div(["Select road: "]),
                __road_picker(dcc, datac, tab_name,'A1',api_base,AIweerfile_functions),           
            ],width=2),
            dbc.Col([
                html.Div(["Select city: "]),
                __city_picker(dcc,weather_data,tab_name,api_base,AIweerfile_functions),        
            ],width=2),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(["Split by: "]),    
                __split_by_picker(dcc,tab_name),
            ],width=2),
            dbc.Col([
                html.Div(["Select weather type: "]),
                __weather_type_picker(dcc, tab_name),
            ],width=2),
        ]),
        
        dcc.Loading(id='loading_weather',children=[
          dcc.Graph(id=("graph_{}").format(tab_name)),   
        ]),
        
    ])
    return weather_tab

def AIWeerFile_tab(dcc,html,dbc,pd,weather_data,datac,api_base,AIweerfile_functions):
    tab_name = 'further'
    new_tab = dcc.Tab(id=tab_name,value=tab_name,label='AIWeerFileDashboard',children=[
        html.H1(children="AIWeerFileDashboard"),
        
        dbc.Stack([
            dbc.Stack([
                html.Div(["Select a year:"]),
                __year_picker(dcc,datac,tab_name,api_base,AIweerfile_functions),
                html.Div(["Select a month: "]),
                __month_picker(dcc,datac,tab_name,api_base,AIweerfile_functions),             
                html.Div(["Or select a specific date range: "]),
                __date_picker(dcc,pd,datac,tab_name,api_base,AIweerfile_functions),
            ],direction="horizontal",gap=3),
            dbc.Stack([
                html.Div(["Select road: "]),
                __road_picker(dcc, datac, tab_name,'A1',api_base,AIweerfile_functions),  
               
                html.Div(["Select city: "]),
                __city_picker(dcc,weather_data,tab_name,api_base,AIweerfile_functions),
            ],direction="horizontal",gap=3),
            dbc.Stack([
                html.Div(["Select traffic information: "]),
                __trafic_information_picker(dcc,tab_name),
                 
                html.Div(["Select statistic: "]),
                __statistic_picker(dcc,tab_name),
                
                html.Div(["Select weather type: "]),
                __weather_type_picker(dcc, tab_name),

                html.Div(["Select plot frequency: "]),
                __frequence_picker(dcc,tab_name),
            ],direction="horizontal",gap=3),   

        ],gap=3),
        
        html.Div([dcc.Markdown('''**Apply filters**''')]),
    
        html.Div(["Select weekdays of interest: "]),
        __weekday_picker(dcc,tab_name),
        
        html.Div(["Select period on the day of interest: "]),
        __period_picker(dcc,tab_name),
         
        html.Div(["Select rootcause: "]),
        __rootcause_picker(dcc,datac,tab_name,api_base,AIweerfile_functions),

        html.Div(["Number of included trafics"]),
        dcc.Textarea(id=('text_{}').format(tab_name)),
        
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
        
        dcc.Store(id='intermediate-value')
        ])
    return new_tab

def heatmap_tab(dcc,html,datac):
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
def __year_picker(dcc,datac,tab_name,api_base,AIweerfile_functions):
    if datac is None:
        unique_years = AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=trafics&columns=year&datecolumn="DateTimeStart"')
    else: 
        unique_years = list(datac.index.year.unique())
    return dcc.Dropdown(['all']+sorted(unique_years), 2024,id=('year_select_{}').format(tab_name),style={'width':'100px'})

def __month_picker(dcc,datac,tab_name,api_base,AIweerfile_functions):
    if datac is None:
        unique_months = AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=trafics&columns=month&datecolumn="DateTimeStart"')
    else:
        unique_months = list(datac.index.month.unique())
    return dcc.Dropdown(['all']+sorted(unique_months), 1,id=('month_select_{}').format(tab_name),style={'width':'100px'})

def __date_picker(dcc,pd,datac,tab_name,api_base,AIweerfile_functions):
    if datac is None:
        min_date = pd.to_datetime(AIweerfile_functions.call_AIWeerFileAPI(api_base,'generic',"?query=SELECT MIN(" + '"DateTimeStart") FROM trafics')[0]).round('D')[0]
        max_date = pd.to_datetime(AIweerfile_functions.call_AIWeerFileAPI(api_base,'generic',"?query=SELECT MAX(" + '"DateTimeStart") FROM trafics')[0]).round('D')[0]
        print(min_date)
    else:
        min_date = datac.index.round('D').min()
        max_date = datac.index.round('D').max()
    return dcc.DatePickerRange(
    id=('date_range_{}').format(tab_name),
    min_date_allowed=min_date,
    max_date_allowed=max_date,
    initial_visible_month=min_date,
    start_date=min_date,
    end_date=max_date,style={'Height':10}
    )
    
def __road_picker(dcc,datac,tab_name,default,api_base,AIweerfile_functions):
    if datac is None:
        unique_roads = AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=trafics&columns="Road"')
    else:
        unique_roads = list(datac.Road.sort_values().unique())
    
    return dcc.Dropdown(['All']+unique_roads,default,id=('road_select_{}').format(tab_name),style={'width':'100px'})
    
def __split_by_picker(dcc,tab_name):
    return dcc.RadioItems(['no_split','direction','ampm','shortlong','weekday'], 'no_split',id=('split_by_{}').format(tab_name),inline=True)
    
def __city_picker(dcc,weather_data,tab_name,api_base,AIweerfile_functions):
    if weather_data is None:
        unique_cities = AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=weather&columns=city')
    else:
        unique_cities = weather_data.city.sort_values().unique()
    return dcc.Dropdown(unique_cities,placeholder='Select another city',id=('city_select_{}').format(tab_name),style={'width':'300px'})
    
def __weather_type_picker(dcc,tab_name):
    return dcc.Dropdown(options={'temperature_2m':'temperature','rain':'rain','snowfall':'snow','precipitation':'precipitation','wind_speed_10m':'wind','sunshine_duration':'sunshine'},value= 'temperature_2m',id=('weather_type_{}').format(tab_name),style={'width':'200px'})

def __trafic_information_picker(dcc,tab_name):
    return dcc.Dropdown(options={'Duration':'duration','GemLengte':'distance'},value='Duration',id=('traffic_information_{}').format(tab_name),style={'width':'200px'})

def __statistic_picker(dcc,tab_name):
    return dcc.Dropdown(['mean','max','min','sum','count'],'mean',id=('statistic_{}').format(tab_name),style={'width':'100px'})

def __weekday_picker(dcc,tab_name):
    return dcc.Checklist({'0':'mon','1':'tue','2':'wed','3':'thu','4':'fri','5':'sat','6':'sun','all':'all days'},['1'],id=('weekday_{}').format(tab_name),inline=True)

def __period_picker(dcc,tab_name):
    return dcc.Checklist({'0-6':'night_morning','6-10':'morning','10-15':'noon','15-19':'evening','19-24':'night-evening','all':'all day'},['all'],id=('period_{}').format(tab_name),inline=True)

def __frequence_picker(dcc,tab_name):
    return dcc.Dropdown(options={'ME':'month','D':'day','h':'hour'},value='D',id=('frequency_{}').format(tab_name),style={'width':'100px'})

def __rootcause_picker(dcc,datac,tab_name,api_base,AIweerfile_functions):
    if datac is None:
        unique_rootcauses = AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=trafics&columns="Oorzaak_4"')
    else:
        unique_rootcauses = datac.Oorzaak_4.unique().tolist()
    return dcc.Checklist(unique_rootcauses,unique_rootcauses,id=('rootcause_{}').format(tab_name),inline=True)