# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 14:16:27 2025

@author: rbijman
"""
def trafic(callback,Output,Input,pd,px,datac):
    tab_name = 'trafic'

    __select_dates(callback,Output,Input,pd,('date_range_{}').format(tab_name),('month_select_{}').format(tab_name))

    @callback(
        Output(('graph_{}1').format(tab_name),'figure'), 
        Output(('graph_{}2').format(tab_name),'figure'),
        Input(('date_range_{}').format(tab_name),'start_date'),
        Input(('date_range_{}').format(tab_name),'end_date'),
        Input(('road_select_{}').format(tab_name),'value'),
        Input(('split_by_{}').format(tab_name),'value')
        )
    def update_output(start_date,end_date,road,split_by):
        if split_by=='no_split':
            split_by=None            
        fig1 = __plot_files_HMpaal(pd,px,datac,start_date,end_date,split_by,road)  
        fig2 = __plot_files_date(pd,px,datac,start_date,end_date,split_by,road)
        return fig1, fig2
            
def weather(callback,Output,Input,pd,px,data,datac):
    tab_name = 'weather_and_trafic'
    __select_dates(callback,Output,Input,pd,('date_range_{}').format(tab_name),('month_select_{}').format(tab_name))

    @callback(
        Output(('graph_{}').format(tab_name),'figure'), 
        Input(('date_range_{}').format(tab_name),'start_date'),
        Input(('date_range_{}').format(tab_name),'end_date'),
        Input(('city_select_{}').format(tab_name),'value'),
        Input(('weather_type_{}').format(tab_name),'value'),
        Input(('road_select_{}').format(tab_name),'value'),
        Input(('split_by_{}').format(tab_name),'value')
        )
    def update_output(start_date,end_date,city,weather_type,road,split_by):
        from plotly.subplots import make_subplots
        if city is None:
            city = datac.query('Road==@road').traject_city.value_counts().index[0]
        if split_by=='no_split':
            split_by=None  
        fig2 = px.line(data.loc[start_date:end_date].query('city==@city')[weather_type],color_discrete_sequence=['green'])                        
        fig2.update_traces(yaxis='y2')
        subfig = make_subplots(specs=[[{"secondary_y": True}]])
        fig1 = __plot_files_date(pd,px,datac,start_date,end_date,split_by,road)
        subfig.add_traces(fig1.data + fig2.data)   
        subfig.update_layout(title_x=0.5,title_text=('Number of trafic on {} between {} and {} vs {} in {}').format(road,pd.to_datetime(start_date).date(),pd.to_datetime(end_date).date(),weather_type,city))        
        return subfig
    
    
def further(callback,Output,Input,pd,px,data,datac):
    tab_name = 'further'
    __select_dates(callback,Output,Input,pd,('date_range_{}').format(tab_name),('month_select_{}').format(tab_name))
 
    @callback(
        Output(('graph_{}').format(tab_name),'figure'), 
        Input(('date_range_{}').format(tab_name),'start_date'),
        Input(('date_range_{}').format(tab_name),'end_date'),
        Input(('city_select_{}').format(tab_name),'value'),
        Input(('weather_type_{}').format(tab_name),'value'),
        Input(('road_select_{}').format(tab_name),'value'),
        Input(('trafic_information_{}').format(tab_name),'value'),
        Input(('statistic_{}').format(tab_name),'value'),
        Input(('weekday_{}').format(tab_name),'value'),
        Input(('frequency_{}').format(tab_name),'value'),
        Input(('rootcause_{}').format(tab_name),'value')
        )
    def update_output(start_date,end_date,city,weather_type,road,trafic_information,statistic,weekday,frequency,rootcause):
        from plotly.subplots import make_subplots
        if city is None:
            city = datac.query('Road==@road').traject_city.value_counts().index[0]
        if 'all' in weekday:
            weekday = ['0','1','2','3','4','5','6']
        plot_data = datac[datac.Oorzaak_4.isin(rootcause)].loc[start_date:end_date].reset_index().query('Road==@road').resample(frequency,on='DateTimeStart')[trafic_information].agg(statistic)
        plot_data = __shift_time_index(plot_data,frequency)
        plot_data = plot_data[plot_data.index.weekday.astype('str').isin(weekday)]
        fig1 = px.bar(plot_data,text=plot_data.index.weekday.astype('str'))#,color_discrete_sequence=['green','red','blue','goldenrod','magenta','orange','brown'])#,color=plot_data.index.weekday.astype('str'))      
        fig1.update_layout(title_x=0.5,barmode='overlay',showlegend=True)
        fig1.update_traces(opacity=0.5,width=__define_bar_width(frequency))
        # plot_data2 = data.loc[start_date:end_date].reset_index().query('city==@city').resample('24h',on='dateandtime')[weather_type].mean()
        # plot_data2 = plot_data2[plot_data2.index.weekday.astype('str').isin(weekday)]
        fig2 = px.line(data[data.index.weekday.astype('str').isin(weekday)].loc[start_date:end_date].query('city==@city')[weather_type],color_discrete_sequence=['green'])                        
        # fig2 = px.line(plot_data2,color_discrete_sequence=['green'])
        fig2.update_traces(yaxis='y2')
        subfig = make_subplots(specs=[[{"secondary_y": True}]])
        subfig.add_traces(fig2.data + fig1.data)
        subfig.update_xaxes({'range': (pd.to_datetime(start_date), pd.to_datetime(end_date))})
        subfig.update_layout(title_x=0.5,title_text=('{} trafic {} on {} between {} and {} vs {} in {}').format(statistic,trafic_information,road,pd.to_datetime(start_date).date(),pd.to_datetime(end_date).date(),weather_type,city))        
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
        end_date = start_date+pd.DateOffset(months=1)-pd.DateOffset(days=1)
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

def __define_bar_width(frequency):
    match frequency:
        case 'ME':
            return 1000*3600*24*30*0.8
        case 'D':
            return 1000*3600*24*0.8
        case 'h':
            return 1000*3600
        
def __shift_time_index(plot_data,frequency):
    match frequency:
        case 'ME':
            return plot_data.shift(14,freq='D')
        case 'D':
            return plot_data.shift(12,freq='h')
        case _:
            return plot_data
    
    
    
    
    
    
    
