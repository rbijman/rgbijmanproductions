# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 14:16:27 2025

@author: rbijman
"""

def trafic(callback,Output,Input,pd,px,datac):

    __select_dates(callback,Output,Input,pd,'date_range_trafic','month_select_trafic')

    @callback(
        Output('graph_trafic1','figure'), 
        Output('graph_trafic2','figure'),
        Input('date_range_trafic','start_date'),
        Input('date_range_trafic','end_date'),
        Input('road_select_trafic','value'),
        Input('split_by_trafic','value')
        )
    def update_output(start_date,end_date,road,split_by):
        if split_by=='no_split':
            split_by=None            
        fig1 = __plot_files_HMpaal(pd,px,datac,start_date,end_date,split_by,road)  
        fig2 = __plot_files_date(pd,px,datac,start_date,end_date,split_by,road)
        return fig1, fig2
            
def weather(callback,Output,Input,pd,px,data,go,datac):

    __select_dates(callback,Output,Input,pd,'date_range_weather','month_select_weather')

    @callback(
        Output('graph_weather','figure'), 
        Input('date_range_weather','start_date'),
        Input('date_range_weather','end_date'),
        Input('city_select','value'),
        Input('weather_type','value'),
        Input('road_select_weather','value'),
        Input('split_by_weather','value')
        )
    def update_output(start_date,end_date,city,weather_type,road,split_by):
        from plotly.subplots import make_subplots
        if split_by=='no_split':
            split_by=None  
        fig2 = px.line(data.loc[start_date:end_date].query('city==@city')[weather_type],color_discrete_sequence=['green'])                        
        fig2.update_traces(yaxis='y2')
        subfig = make_subplots(specs=[[{"secondary_y": True}]])
        fig1 = __plot_files_date(pd,px,datac,start_date,end_date,split_by,road)
        subfig.add_traces(fig1.data + fig2.data)        
        return subfig
    

#Helper functions

def __select_dates(callback,Output,Input,pd,date_range_id,month_select_id):
    @callback(
        Output(date_range_id,'start_date'),
        Output(date_range_id,'end_date'),
        Input(month_select_id,'value')    
        )
    def update_start_date(month):
        start_date= pd.to_datetime(('2024-{}').format(month))
        end_date = start_date+pd.DateOffset(months=1)
        return start_date, end_date
    
def __plot_files_HMpaal(pd,px,datac,start_date,end_date,split_by,road):
    fig = px.histogram(datac.loc[start_date:end_date].query('Road==@road').explode('HPrange'),x='HPrange',color=split_by,
                       nbins=200,
                       labels='counts',
                       title=('Number of Trafics on {} between {} and {} per HMpaal').format(road,pd.to_datetime(start_date).date(),pd.to_datetime(end_date).date())
                       )
    fig.update_layout(title_x=0.5,barmode='overlay',showlegend=True)
    fig.update_traces(opacity=0.5)
    if len(fig['data'])==1:
        fig['data'][0]['showlegend']=True
        fig['data'][0]['name']='Number of Trafics'
    
    
    return fig
    
def __plot_files_date(pd,px,datac,start_date,end_date,split_by,road):
    fig = px.histogram(datac.loc[start_date:end_date].query('Road==@road').reset_index(),x='DateTimeStart',color=split_by,
                       nbins=1000,
                       labels='counts',
                       title=('Number of Trafics on {} between {} and {}').format(road,pd.to_datetime(start_date).date(),pd.to_datetime(end_date).date())
                       )
    fig.update_layout(title_x=0.5,barmode='overlay',showlegend=True)
    fig.update_traces(opacity=0.5)
    if len(fig['data'])==1:
        fig['data'][0]['showlegend']=True
        fig['data'][0]['name']='Number of Trafics'
    return fig
    
    
