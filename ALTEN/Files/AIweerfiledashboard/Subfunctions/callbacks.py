# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 14:16:27 2025

@author: rbijman
"""
def trafic(callback,Output,Input,pd,px,datac):
    tab_name = 'traffic'

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
    tab_name = 'weather_and_traffic'
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
            city = datac.query('Road in @road').traject_city.value_counts().index[0]
        if split_by=='no_split':
            split_by=None  
        fig2 = px.line(data.loc[start_date:end_date].query('city==@city')[weather_type],color_discrete_sequence=['green'])                        
        fig2.update_traces(yaxis='y2')
        subfig = make_subplots(specs=[[{"secondary_y": True}]])
        fig1 = __plot_files_date(pd,px,datac,start_date,end_date,split_by,road)
        subfig.add_traces(fig1.data + fig2.data)   
        subfig.update_layout(title_x=0.5,title_text=('Number of traffic on {} between {} and {} vs {} in {}').format(road,pd.to_datetime(start_date).date(),pd.to_datetime(end_date).date(),weather_type,city))        
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
        Input(('traffic_information_{}').format(tab_name),'value'),
        Input(('statistic_{}').format(tab_name),'value'),
        Input(('weekday_{}').format(tab_name),'value'),
        Input(('frequency_{}').format(tab_name),'value'),
        Input(('rootcause_{}').format(tab_name),'value'),
        Input(('excluded_traffics_{}').format(tab_name),'value')
        )
    def update_output(start_date,end_date,city,weather_type,road,traffic_information,statistic,weekday,frequency,rootcause,excluded_traffics):
        from plotly.subplots import make_subplots
        if road=='All':
            road=list(datac.Road.unique())
            plot_title_road='All roads'
        else:
            plot_title_road=road
        if city is None:
            city = datac.query('Road in @road').traject_city.value_counts().index[0]
        if 'all' in weekday:
            weekday = ['0','1','2','3','4','5','6']
        
        plot_data = datac.copy()
        if 'grens' in excluded_traffics:
            plot_data = plot_data.query('not traject.str.contains("grens")') #exclude grens
        if '>50km' in excluded_traffics:
            plot_data = plot_data.query('not GemLengte>50')
        plot_data = plot_data[plot_data.Oorzaak_4.isin(rootcause)].loc[start_date:end_date].reset_index().query('Road in @road').resample(frequency,on='DateTimeStart')[traffic_information].agg(statistic)
        plot_data = __shift_time_index(plot_data,frequency)
        plot_data = plot_data[plot_data.index.weekday.astype('str').isin(weekday)]
        
        
        fig1 = px.bar(plot_data,text=plot_data.index.weekday.astype('str'))#,color_discrete_sequence=['green','red','blue','goldenrod','magenta','orange','brown'])#,color=plot_data.index.weekday.astype('str'))      
        fig1.update_layout(title_x=0.5,barmode='overlay',showlegend=True)
        fig1.update_traces(opacity=0.5,width=__define_bar_width(frequency))
        fig2 = px.line(data[data.index.weekday.astype('str').isin(weekday)].loc[start_date:end_date].query('city==@city')[weather_type],color_discrete_sequence=['green'])                        
        fig2.update_traces(yaxis='y2',opacity=0.5)
        subfig = make_subplots(specs=[[{"secondary_y": True}]])
        subfig.add_traces(fig2.data + fig1.data)
        subfig.update_xaxes({'range': (pd.to_datetime(start_date), pd.to_datetime(end_date))})
        subfig.update_layout(title_x=0.5,title_text=('{} traffic {} on {} between {} and {} vs {} in {}').format(statistic,traffic_information,plot_title_road,pd.to_datetime(start_date).date(),pd.to_datetime(end_date).date(),weather_type,city))        
        
        return subfig#, subfig2
    

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
                       title=('Number of Traffics on {} between {} and {} per HMpaal').format(road,pd.to_datetime(start_date).date(),pd.to_datetime(end_date).date())
                       )
    fig.update_layout(title_x=0.5,barmode='overlay',showlegend=True)
    fig.update_traces(opacity=0.75)
    if len(fig['data'])==1:
        fig['data'][0]['showlegend']=True
        fig['data'][0]['name']='Number of Traffics'
    
    
    return fig
    
def __plot_files_date(pd,px,datac,start_date,end_date,split_by,road):
    fig = px.histogram(datac.loc[start_date:end_date].query('Road==@road').reset_index(),x='DateTimeStart',color=split_by,
                       nbins=1000,
                       labels='counts',
                       title=('Number of Traffics on {} between {} and {}').format(road,pd.to_datetime(start_date).date(),pd.to_datetime(end_date).date())
                       )
    fig.update_layout(title_x=0.5,barmode='overlay',showlegend=True)
    fig.update_traces(opacity=0.5)
    if len(fig['data'])==1:
        fig['data'][0]['showlegend']=True
        fig['data'][0]['name']='Number of Traffics'
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
        
def __plot_on_map(pd,px,datac,data):
    import geopandas as gpd
    url1 = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    world = gpd.read_file(url1)[['SOV_A3', 'POP_EST', 'CONTINENT', 'NAME', 'GDP_MD', 'geometry']]
    world = world.set_index("SOV_A3")
    
    from plotly.subplots import make_subplots
    subfig = make_subplots()
    
    fig1 = world.query('SOV_A3=="NL1"').plot()
    fig2 = px.scatter(datac.query('Road=="A4"').groupby(by=['lat_middle','lon_middle']).Duration.mean().reset_index(),x='lon_middle',y='lat_middle',c='Duration')
    cities_of_interest = ['Utrecht','Amsterdam','Rotterdam','Gouda','Eindhoven','Zwolle','Groningen','Maastricht']
    test = data.query("city in @cities_of_interest")
    
    subfig.add_traces(fig1,fig2)

    for idx,city in enumerate(test.city):
        subfig.add_annotation(text=test.city.iloc[idx], x=test.lon.iloc[idx],y=test.lat.iloc[idx])
    return subfig
    
    
    
    
    
    
