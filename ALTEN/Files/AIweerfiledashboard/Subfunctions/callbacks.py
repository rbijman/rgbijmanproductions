# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 14:16:27 2025

@author: rbijman
"""

def trafic(callback,Output,Input,pd,px,datac):

    __select_dates(callback,Output,Input,pd,'date_range_trafic','month_select_trafic')

    @callback(
        Output('graph_trafic','figure'), 
        # Output('month_select','value'),
        Input('date_range_trafic','start_date'),
        Input('date_range_trafic','end_date'),
        Input('road_select','value'),
        Input('split_by','value')
        )
    def update_output(start_date,end_date,road,split_by):
        if split_by=='no_split':
            split_by=None
        fig = px.histogram(datac.loc[start_date:end_date].query('Road==@road').explode('HPrange'),x='HPrange',color=split_by,
                           nbins=200,
                           labels='counts',
                           title=('Number of Trafics on {} between {} and {}').format(road,pd.to_datetime(start_date).date(),pd.to_datetime(end_date).date())
                           )
        fig.update_layout(title_x=0.5,barmode='overlay')
        fig.update_traces(opacity=0.5)                        
        return fig
    
def weather(callback,Output,Input,pd,px,data):

    __select_dates(callback,Output,Input,pd,'date_range_weather','month_select_weather')

    @callback(
        Output('graph_weather','figure'), 
        # Output('month_select','value'),
        Input('date_range_weather','start_date'),
        Input('date_range_weather','end_date'),
        Input('city_select','value'),
        # Input('split_by','value')
        )
    def update_output(start_date,end_date,city):
        fig = px.line(data.loc[start_date:end_date].query('city==@city').temperature_2m)                       
        return fig
    

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
    
    
