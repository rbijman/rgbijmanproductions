# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 14:16:27 2025

@author: rbijman
"""
def main(callback, Output, Input, pd, px, weather_data,datac,working_dir,api_base,AIweerfile_functions):
    AIWeerFile(callback, Output, Input, pd, px, weather_data,datac,working_dir,api_base,AIweerfile_functions)
    update_data(callback, Output, Input, working_dir,AIweerfile_functions)
    # traffic(callback,Output,Input,pd,px,datac,working_dir,api_base,AIweerfile_functions)
    # weather(callback,Output,Input,pd,px,weather_data,datac,api_base,AIweerfile_functions)

def update_data(callback,Output,Input,working_dir,AIweerfile_functions):
    tab_name = 'update_data'
    @callback(
        Output(('loading_status_{}').format(tab_name),'value'),
        Input('update_traffic_sql_button','n_clicks'),
        Input('update_weather_sql_button','n_clicks'),
        Input('update_pickle_button','n_clicks'),
        Input(('date_range_{}').format(tab_name),'start_date'),
        Input(('date_range_{}').format(tab_name),'end_date'),
        Input('input_shortlong_border','value'),
        Input('input_ampm_border','value')
        )
    def update_output(btn1,btn2,btn3,start_date,end_date,shortlong_border,ampm_border):       
        #update sql database contents with new data
        print_message = 'no data update done yet'
        if btn1>0 or btn2>0:          
            datac, lat_lon_df, weather_per_city = AIweerfile_functions.collect_and_clean_AIweerfiledata(start_date,end_date,ampm_border,shortlong_border)  
            # datac.columns = datac.columns.str.lower()
            if btn1>0:
                sql_table_to_update = 'trafics'
                print_message = 'SQL traffic table updated'
                data_to_update = datac
                AIweerfile_functions.update_sql_database(working_dir,AIweerfile_functions,data_to_update,sql_table_to_update)
            elif btn2>0:
                sql_table_to_update = 'weather'
                print_message = 'SQL weather table updated'
                data_to_update = weather_per_city
                AIweerfile_functions.update_sql_database(working_dir,AIweerfile_functions,data_to_update,sql_table_to_update)
            print(print_message)

        
        #update pickle with sql database contents
        if btn3>0:
            datac_file_path = working_dir + r"\ProcessedData\datac"
            AIweerfile_functions.update_pickle_with_sql_database_data(AIweerfile_functions,working_dir,datac_file_path,'trafics')
            weather_per_city_path = working_dir + r"\ProcessedData\weather_data"
            AIweerfile_functions.update_pickle_with_sql_database_data(AIweerfile_functions,working_dir,weather_per_city_path,'weather')
            print_message('pickles updated')
            
        return print_message

def traffic(callback,Output,Input,pd,px,datac,working_dir,api_base,AIweerfile_functions):
    tab_name = 'traffic'

    __select_dates(callback,Output,Input,pd,('date_range_{}').format(tab_name),('month_select_{}').format(tab_name),('year_select_{}').format(tab_name),datac,api_base,AIweerfile_functions)

    @callback(
        Output(('graph_{}1').format(tab_name),'figure'), 
        Output(('graph_{}2').format(tab_name),'figure'),
        Input(('date_range_{}').format(tab_name),'start_date'),
        Input(('date_range_{}').format(tab_name),'end_date'),
        Input(('road_select_{}').format(tab_name),'value'),
        Input(('split_by_{}').format(tab_name),'value'),
        Input(('excluded_traffics_{}').format(tab_name),'value')
        )
    def update_output(start_date,end_date,road,split_by,excluded):
        if split_by=='no_split':
            split_by=None
            
        fig1 = __plot_files_HMpaal(pd,px,datac,start_date,end_date,split_by,road,excluded,working_dir,AIweerfile_functions)  
        fig2 = __plot_files_date(pd,px,datac,start_date,end_date,split_by,road)
        return fig1, fig2
            
def weather(callback,Output,Input,pd,px,weather_data,datac,api_base,AIweerfile_functions):
    tab_name = 'weather_and_traffic'
    __select_dates(callback,Output,Input,pd,('date_range_{}').format(tab_name),('month_select_{}').format(tab_name),('year_select_{}').format(tab_name),datac,api_base,AIweerfile_functions)

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
        fig2 = px.line(weather_data.loc[start_date:end_date].query('city==@city')[weather_type],color_discrete_sequence=['green'])                        
        fig2.update_traces(yaxis='y2')
        subfig = make_subplots(specs=[[{"secondary_y": True}]])
        fig1 = __plot_files_date(pd,px,datac,start_date,end_date,split_by,road)
        subfig.add_traces(fig1.data + fig2.data)   
        subfig.update_layout(title_x=0.5,title_text=('Number of traffic on {} between {} and {} vs {} in {}').format(road,pd.to_datetime(start_date).date(),pd.to_datetime(end_date).date(),weather_type,city))        
        return subfig
    
def AIWeerFile(callback,Output,Input,pd,px,weather_data,datac,working_dir,api_base,AIweerfile_functions):
    tab_name = 'further'
    __select_dates(callback,Output,Input,pd,('date_range_{}').format(tab_name),('month_select_{}').format(tab_name),('year_select_{}').format(tab_name),datac,api_base,AIweerfile_functions)
 
    @callback(
        Output(('graph_{}').format(tab_name),'figure'),
        Output(('text_{}').format(tab_name),'value'),
        Output(('total_pandas_query_{}').format(tab_name),'value'),
        Output(('total_api_query_{}').format(tab_name),'value'),
        Output(('graph2_{}').format(tab_name),'figure'),
        Output(("initial_spinner_{}").format(tab_name), "style"),
        # Output('graph_heatmap','figure'),
        Input(('date_range_{}').format(tab_name),'start_date'),
        Input(('date_range_{}').format(tab_name),'end_date'),
        Input(('city_select_{}').format(tab_name),'value'),
        Input(('weather_type_{}').format(tab_name),'value'),
        Input(('road_select_{}').format(tab_name),'value'),
        Input(('traffic_information_{}').format(tab_name),'value'),
        Input(('statistic_{}').format(tab_name),'value'),
        Input(('weekday_{}').format(tab_name),'value'),
        Input(('period_{}').format(tab_name),'value'),
        Input(('frequency_{}').format(tab_name),'value'),
        Input(('rootcause_{}').format(tab_name),'value'),
        Input(("graph_{}").format(tab_name),'clickData')
        # Input(('excluded_traffics_{}').format(tab_name),'value') NOT IN USE ANYMORE
        )
    def update_output(start_date,end_date,city,weather_type,road,traffic_information,statistic,weekday,period,frequency,rootcause,clickdata):
        
        from plotly.subplots import make_subplots
        # AIweerfile_functions = __import_AIweerfile_functions(working_dir)

        road,city,weekday,period,plot_title_road = __prep_inputs(road,city,weekday,period,datac,api_base,AIweerfile_functions)
      
        #query the datac into plot_data
        traffic_table_name = 'trafics'
        traffic_columns =  ' , '.join(['"DateTimeStart"','"Road"','"direction"','"shortlong"','"ampm"']) + ' , ' + '"' + traffic_information + '"'        
        weather_table_name = 'weather'
        weather_columns = ' , '.join(['date']) + ' , ' + '"' + weather_type + '"'
        total_pandas_traffic_query,total_api_traffic_query,total_pandas_weather_query,total_API_weather_query = __combine_all_queries(period,weekday,rootcause,road,city,pd.to_datetime(start_date),pd.to_datetime(end_date),traffic_table_name,traffic_columns,weather_table_name,weather_columns)
        
        if datac is None:
            data = AIweerfile_functions.call_AIWeerFileAPI(api_base,'main',total_api_traffic_query)
            queried_data = pd.DataFrame(data['data'],columns=data['columns'])
            queried_data['DateTimeStart'] = pd.to_datetime(queried_data['DateTimeStart'])
            queried_data = queried_data.sort_values('DateTimeStart').set_index('DateTimeStart')
            del data
            print(queried_data.shape)
        else:
            queried_data = datac.query(total_pandas_traffic_query).loc[start_date:end_date]
        
        nr_of_traffics_included = str(queried_data.shape[0])
        #resample the data
        plot_data = queried_data.reset_index().resample(frequency,on='DateTimeStart')[traffic_information].agg(statistic)
        plot_data = __shift_time_index(plot_data,frequency).to_frame()
        
        color_dict = {0:'blue',1:'red',2:'green',3:'orange',4:'black',5:'gold',6:'pink'}
        c = plot_data.index.weekday.map(color_dict)
        
        if weather_data is None:
            temp_data = AIweerfile_functions.call_AIWeerFileAPI(api_base,'main',total_API_weather_query)
            weather_plot_data = pd.DataFrame(temp_data['data'],columns=temp_data['columns'])
            weather_plot_data['date'] = pd.to_datetime(weather_plot_data['date'])
            weather_plot_data = weather_plot_data.sort_values('date').set_index('date')[weather_type]
            del temp_data
        else:
            weather_plot_data = weather_data.query(total_pandas_weather_query).loc[start_date:end_date][weather_type]        
     
        #plotting
        fig1 = px.bar(plot_data,text=plot_data.index.weekday.astype('str'))#,color_discrete_sequence=['green','red','blue','goldenrod','magenta','orange','brown'])#,color=plot_data.index.weekday.astype('str'))      
        fig1.update_layout(title_x=0.5,barmode='overlay',showlegend=False)
        fig1.update_traces(opacity=0.5,width=__define_bar_width(frequency),marker_color=c)
        fig2 = px.line(weather_plot_data,color_discrete_sequence=['green'])                        
        fig2.update_traces(yaxis='y2',opacity=0.5)
        subfig = make_subplots(specs=[[{"secondary_y": True}]])
        subfig.add_traces(fig2.data + fig1.data)
        subfig.update_xaxes({'range': (pd.to_datetime(start_date), pd.to_datetime(end_date))})
        subfig.update_layout(yaxis_title=('{} {}').format(statistic,traffic_information))
        subfig.update_layout(yaxis2_title = weather_type)
        subfig.update_layout(title_x=0.5,title_text=('{} traffic {} on {} between {} and {} vs {} in {}').format(statistic,traffic_information,plot_title_road,pd.to_datetime(start_date).date(),pd.to_datetime(end_date).date(),weather_type,city))        
        
        
        total_pandas_query_output = 'datac.query("' + total_pandas_traffic_query+ '")' + '.loc["'+pd.to_datetime(start_date).strftime('%Y-%m-%d').replace('-0','-')+'":"'+pd.to_datetime(end_date).strftime('%Y-%m-%d').replace('-0','-')+'"]'
                
        if clickdata != None:
            date1,date2 = __define_datetime_range(clickdata,frequency,pd)  
            print(date1)
            print(date2)
            plot_data_fig3 = queried_data.loc[date1:date2]
        else:
            date1 = start_date
            date2 = end_date
            plot_data_fig3 = queried_data
        fig3 = px.bar(plot_data_fig3.groupby('Road')[traffic_information].agg(statistic).sort_values(ascending=False))
        fig3.update_layout(title_x=0.5,title_text=('{} traffic {} on {} between {} and {}').format(statistic,traffic_information,plot_title_road,date1,date2))
        fig3.update_layout(yaxis_title=('{} {}').format(statistic,traffic_information))
        
        # #heatmap plotting
        # op_vs_af = pd.crosstab(queried_data.Road,queried_data.direction,queried_data[traffic_information],aggfunc=statistic,dropna=True).fillna(pd.NA)  
        # short_vs_long = pd.crosstab(queried_data.Road,queried_data.shortlong,queried_data[traffic_information],aggfunc=statistic).fillna(pd.NA)  
        # am_vs_pm = pd.crosstab(queried_data.Road,queried_data.ampm,queried_data[traffic_information],aggfunc=statistic).fillna(pd.NA)   
        # # per_weekday = pd.crosstab(queried_data.Road,queried_data.DateTimeStart.sort_values().dt.day_name().apply(lambda x:x[0:3]),datac[traffic_information],aggfunc=statistic)[['Mon','Thu','Wed','Thu','Fri','Sat','Sun']].fillna(pd.NA)  
        # # per_month = pd.crosstab(queried_data.Road,queried_data.DateTimeStart.sort_values().dt.month_name().apply(lambda x: x[0:3]),datac[traffic_information],aggfunc=statistic).fillna(pd.NA)  
        # rainy_vs_dry = pd.crosstab(queried_data.Road,queried_data.rainydry,queried_data[traffic_information],aggfunc=statistic).fillna(pd.NA)
        # temp_cat = pd.crosstab(queried_data.Road,queried_data.temp_cat,queried_data[traffic_information],aggfunc=statistic).fillna(pd.NA)

        # # trafic_per_cat = pd.concat([op_vs_af,short_vs_long,am_vs_pm,per_weekday,per_month,temp_cat,rainy_vs_dry],axis=1)
        # trafic_per_cat = pd.concat([op_vs_af,short_vs_long,am_vs_pm,temp_cat,rainy_vs_dry],axis=1)
        # trafic_per_cat['Total'] = queried_data.groupby('Road')[traffic_information].agg(statistic)   
        # trafic_per_cat_ranked= trafic_per_cat.rank(ascending=False,method='max').sort_values(by='Total')
        # heatmap = px.imshow(trafic_per_cat_ranked.T)
         
        return subfig,nr_of_traffics_included,total_pandas_query_output,total_api_traffic_query,fig3,{"display": "none"}#,heatmap
    
    @callback(
        Output("graph_{}".format(tab_name), "clickData"),
        Input("graph_field", "n_clicks")
        )
    def reset_clickData(n_clicks):
        return None

#Helper functions

def __select_dates(callback,Output,Input,pd,date_range_id,month_select_id,year_select_id,datac,api_base,AIweerfile_functions):
    @callback(
        Output(date_range_id,'start_date'),
        Output(date_range_id,'end_date'),
        Input(year_select_id,'value'),
        Input(month_select_id,'value')    
        )
    def update_start_date(year,month):
        if month == 'all':
            if datac is None:
                start_date = pd.to_datetime(AIweerfile_functions.call_AIWeerFileAPI(api_base,'generic',"?query=SELECT MIN(" + '"DateTimeStart") FROM trafics')[0]).round('D')[0]
                end_date = pd.to_datetime(AIweerfile_functions.call_AIWeerFileAPI(api_base,'generic',"?query=SELECT MAX(" + '"DateTimeStart") FROM trafics')[0]).round('D')[0]
            else:
                start_date = pd.to_datetime(datac.index.min())
                end_date = pd.to_datetime(datac.index.max())
        else:
            start_date= pd.to_datetime(('{}-{}').format(year,month))
            end_date = start_date+pd.DateOffset(months=1)-pd.DateOffset(days=1)
        return start_date, end_date
    
def __period_select(period):
    period_total = []
    if '0-6' in period:
        period_total += list(range(0,7))
    if '6-10' in period:
        period_total += list(range(7,10))
    if '10-15' in period:
        period_total += list(range(10,15))
    if '15-19' in period:
        period_total += list(range(15,19))
    if '19-24' in period:
        period_total += list(range(19,25))
            
    return period_total
    
def __plot_files_HMpaal(pd,px,datac,start_date,end_date,split_by,road,excluded,working_dir,AIweerfile_functions):
    # AIweerfile_functions = __import_AIweerfile_functions(working_dir)
    datac['HPrange'] = datac.apply(lambda x: AIweerfile_functions.getHPrange(x['HPstart'],x['HPend']),axis=1)

    
    excluded_query = 'index==index'
    if 'grens' in excluded:
        excluded_query = 'not traject.str.contains("grens")'
    if '>25km' in excluded:
        excluded_query = 'not distance>25'
    
    fig = px.histogram(datac.query(excluded_query).loc[start_date:end_date].query('Road==@road').explode('HPrange'),x='HPrange',color=split_by,
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
            return plot_data.shift(-14,freq='D')
        case 'D':
            return plot_data.shift(12,freq='h')
        case _:
            return plot_data
        
def __combine_all_queries(period,weekday,rootcause,road,city,start_date,end_date,traffic_table_name,traffic_columns,weather_table_name,weather_columns):#excluded_traffics):
    from datetime import timedelta
    
    #Pandas query
    periods_total = __period_select(period)
    period_query = ('index.dt.hour.isin({})').format(periods_total)
    weekday_query = ("index.dt.weekday.astype('str').isin({})").format(weekday)
    root_cause_query = ('Oorzaak_4.isin({})').format(rootcause)
    road_query = ('Road in {}').format(road)
    city_query = ('city== "{}"').format(city)
    # excluded_query = 'index==index'
    # if 'grens' in excluded_traffics:
    #     excluded_query = 'not traject.str.contains("grens")'
    # if '>50km' in excluded_traffics:
    #     excluded_query = 'not GemLengte>50'
    
    total_pandas_traffic_query = period_query + ' & ' + weekday_query + ' & ' + root_cause_query + ' & ' + road_query #+ ' & ' + excluded_query 
    total_pandas_weather_query = weekday_query + ' & ' + period_query + ' & ' + city_query

    
    period_filter = '&hours=' + (', '.join(map(str, periods_total)))
    road_filter = '&"Road"=' + (', '.join(map(str, road)))
    weekday_filter = '&weekdays=' + (', '.join(map(str, weekday)))
    start_date_filter ='&start_date=' + start_date.strftime('%Y-%m-%d')#.replace('-0','-')
    end_date_filter = '&end_date=' + (end_date+timedelta(days=1)).strftime('%Y-%m-%d')#.replace('-0','-')
    rootcause_filter = '&"Oorzaak_4"=' + (', '.join(map(str, rootcause)))
    city_filter = '&city=' + city
    
    total_API_traffic_query = '?table=' + traffic_table_name + '&' + 'columns=' + traffic_columns + '&' + 'datecolumn="DateTimeStart"' + start_date_filter + end_date_filter + period_filter + road_filter + weekday_filter + rootcause_filter
    total_API_weather_query = '?table=' + weather_table_name + '&' + 'columns=' + weather_columns + '&' + 'datecolumn=date' + start_date_filter + end_date_filter + period_filter + city_filter + weekday_filter
    print(total_API_traffic_query)
    print(total_API_weather_query)
    return total_pandas_traffic_query, total_API_traffic_query, total_pandas_weather_query, total_API_weather_query
    
    
def __prep_inputs(road,city,weekday,period,datac,api_base,AIweerfile_functions):
    if road=='All':
        if datac is None:
            road = AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=trafics&columns="Road"')
        else: 
            road=list(datac.Road.unique())
        plot_title_road='All roads'
    else:
        road = [road]
        plot_title_road=road[0]
    if city is None:
        if datac is None:
            if len(road)==1:
                tuple_road = tuple(road+road)
            else:
                tuple_road = tuple(road)
            city = AIweerfile_functions.call_AIWeerFileAPI(api_base,'generic','?query=SELECT traject_city, COUNT(*) as count FROM trafics WHERE "Road" IN' +f"{tuple_road} GROUP BY traject_city ORDER BY count DESC LIMIT 1")[0][0]
        else:
            city = datac.query('Road in @road').traject_city.value_counts().index[0]
    if 'all' in weekday:
        weekday = ['0','1','2','3','4','5','6']
    if 'all' in period:
        period = ['0-6','6-10','10-15','15-19','19-24']    
    return    road,city,weekday,period,plot_title_road

def __define_datetime_range(clickdata,frequency,pd):
    timestamp = pd.to_datetime(clickdata['points'][0]['x'])
    match frequency:
        case 'ME':
            date1 = timestamp.floor('d').date().strftime('%Y-%m-01')
            date2 = timestamp.floor('d').date().strftime(('%Y-%m-{}').format(timestamp.days_in_month))
        case 'D':
            date1 = timestamp.floor('d').date().strftime('%Y-%m-%d')
            date2 = date1
    return date1,date2






### NOT IN USE NOW  

# def __plot_on_map(pd,px,datac,weather_data):
#     import geopandas as gpd
#     url1 = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
#     world = gpd.read_file(url1)[['SOV_A3', 'POP_EST', 'CONTINENT', 'NAME', 'GDP_MD', 'geometry']]
#     world = world.set_index("SOV_A3")
    
#     from plotly.subplots import make_subplots
#     subfig = make_subplots()
    
#     fig1 = world.query('SOV_A3=="NL1"').plot()
#     fig2 = px.scatter(datac.query('Road=="A4"').groupby(by=['lat_middle','lon_middle']).Duration.mean().reset_index(),x='lon_middle',y='lat_middle',c='Duration')
#     cities_of_interest = ['Utrecht','Amsterdam','Rotterdam','Gouda','Eindhoven','Zwolle','Groningen','Maastricht']
#     test = weather_data.query("city in @cities_of_interest")
    
#     subfig.add_traces(fig1,fig2)

#     for idx,city in enumerate(test.city):
#         subfig.add_annotation(text=test.city.iloc[idx], x=test.lon.iloc[idx],y=test.lat.iloc[idx])
#     return subfig

# def __import_AIweerfile_functions(working_dir):
#     import sys
#     sys.path.insert(0,working_dir + r"\AIweerfiledashboard\Subfunctions")
#     import AIweerfile_functions
#     return AIweerfile_functions