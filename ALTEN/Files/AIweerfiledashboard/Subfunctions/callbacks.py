# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 14:16:27 2025

@author: rbijman
"""
def main(callback, Output, Input, State, pd, px, weather_data,datac,working_dir,api_base,AIweerfile_functions,callback_context):
    get_dropdown_options(callback,Output,Input,pd,datac,weather_data,api_base,AIweerfile_functions)
    AIWeerFile(callback, Output, Input, State, pd, px, weather_data,datac,working_dir,api_base,AIweerfile_functions,callback_context)
    update_data(callback, Output, Input, working_dir,AIweerfile_functions)
    # traffic(callback,Output,Input,pd,px,datac,working_dir,api_base,AIweerfile_functions)
    # weather(callback,Output,Input,pd,px,weather_data,datac,api_base,AIweerfile_functions)

# Callback to query the data once on app load and store it
def get_dropdown_options(callback,Output,Input,pd,datac,weather_data,api_base,AIweerfile_functions):
    @callback(
        Output('dropdown_options_store', 'data'),
        [Input('dropdown_options_store', 'data')]
    )
    def load_dropdown_options_on_app_load(dropdown_options):
        if dropdown_options is None:
            dropdown_options = __get_dropdown_options(pd,datac,weather_data,api_base,AIweerfile_functions)    
        return dropdown_options


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
    
def AIWeerFile(callback,Output,Input,State,pd,px,weather_data,datac,working_dir,api_base,AIweerfile_functions,callback_context):
    tab_name = 'further'
    dropdown_menus_to_populate = {'roads':'road_select_'+tab_name,'years':'year_select_'+tab_name,'months':'month_select_'+tab_name, 'date_range':['date_range_'+tab_name,'min_date_allowed','max_date_allowed'],'rootcauses':'rootcause_' + tab_name,'cities':'city_select_' + tab_name}
    for dropdown_type, dropdown_id in dropdown_menus_to_populate.items():
            __populate_dropdown_menu(callback,Output,Input,dropdown_type,dropdown_id)
    __select_dates(callback,Output,Input,pd,('date_range_{}').format(tab_name),('month_select_{}').format(tab_name),('year_select_{}').format(tab_name),datac,api_base,AIweerfile_functions)
        
    @callback(
        # Output(('current_data_{}').format(tab_name),'data'),
        # Output(('current_weather_data_{}').format(tab_name),'data'),
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
        Input(('statistic_traffic_{}').format(tab_name),'value'),
        Input(('weekday_{}').format(tab_name),'value'),
        Input(('period_{}').format(tab_name),'value'),
        Input(('frequency_traffic_{}').format(tab_name),'value'),
        Input(('rootcause_{}').format(tab_name),'value'),
        Input(('statistic_weather_{}').format(tab_name),'value'),
        Input(('frequency_weather_{}').format(tab_name),'value'),      
        Input(('weather_marker_size_{}').format(tab_name),'value'),
        Input(("graph_{}").format(tab_name),'clickData'),
        Input(("subtract_weekday_average_{}").format(tab_name),'value'),
        # State(('current_data_{}').format(tab_name), 'data'),
        # State(('current_weather_data_{}').format(tab_name), 'data')
        )
    def update_output(start_date,end_date,city,weather_type,road,traffic_information,statistic_traffic,weekday,period,frequency_traffic,rootcause,statistic_weather,frequency_weather,weather_marker_size,clickdata,subtract_weekday_average):
        from plotly.subplots import make_subplots
        current_traffic_data = []
        inputs = __prep_inputs(road,city,weekday,period,rootcause,start_date,end_date,datac,api_base,AIweerfile_functions)
        triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0] if callback_context.triggered else None
        
        #Define which callback triggers should reload the data for traffic and for weather data
        traffic_trigger_id_list = ['date_range','road_select','traffic_information','weekday','period','rootcause']
        traffic_trigger_id_list = [item + f'_{tab_name}' for item in traffic_trigger_id_list]
        weather_trigger_id_list = ['date_range','city_select','weather_type','weekday','period']
        weather_trigger_id_list = [item + f'_{tab_name}' for item in weather_trigger_id_list]
        
        #query the data into plot_data
        traffic_table_name = 'trafics'
        traffic_columns =  ' , '.join(['"DateTimeStart"','"Road"','"direction"','"shortlong"','"ampm"']) + ' , ' + '"' + traffic_information + '"'        
        weather_table_name = 'weather'
        weather_columns = ' , '.join(['date']) + ' , ' + '"' + weather_type + '"'
        all_queries = __combine_all_queries(inputs,traffic_table_name,traffic_columns,weather_table_name,weather_columns,pd)
        # queried_data,inputs,all_queries = __load_all_data(datac,weather_data,triggered_id,api_base,AIweerfile_functions,pd,current_traffic_data,start_date,end_date,traffic_trigger_id_list,weather_trigger_id_list,traffic_table_name,traffic_columns,weather_table_name,weather_columns,road,city,weekday,period,rootcause)
        queried_data = __load_all_data(datac,weather_data,triggered_id,all_queries,api_base,AIweerfile_functions,pd,current_traffic_data,start_date,end_date,traffic_trigger_id_list,weather_trigger_id_list,traffic_table_name,traffic_columns,weather_table_name,weather_columns,road,city,weekday,period,rootcause)
        
        print(queried_data['traffic'].info())
        
        queried_traffic_data = queried_data['traffic']#.sort_values('DateTimeStart').set_index('DateTimeStart')
        queried_weather_data = queried_data['weather']#.sort_values('date').set_index('date')[weather_type]

        
        #resample the data
        traffic_plot_data = queried_traffic_data.reset_index().resample(frequency_traffic,on='DateTimeStart')[traffic_information].agg(statistic_traffic).dropna()
        traffic_plot_data = __shift_time_index(traffic_plot_data,frequency_traffic).to_frame()
        weather_plot_data = queried_weather_data.reset_index().resample(frequency_weather,on='date')[weather_type].agg(statistic_weather)
        weather_plot_data = __shift_time_index(weather_plot_data,frequency_weather).to_frame().dropna()
        
        print(weather_plot_data.info())
        print(traffic_plot_data.info())
        if 'on' in subtract_weekday_average:
            traffic_plot_data[traffic_information] = traffic_plot_data[traffic_information] - traffic_plot_data.groupby(traffic_plot_data.index.weekday)[traffic_information].transform('mean')
        
        color_dict = {0:'blue',1:'red',2:'green',3:'orange',4:'black',5:'gold',6:'pink'}
        c = traffic_plot_data.index.weekday.map(color_dict)
        
        # Aligning the series based on their indexes (intersection of dates)
        df_aligned = traffic_plot_data.join(weather_plot_data, how='inner')  # 'inner' will align only common dates
        
        # Calculate the correlation
        from scipy.stats import pearsonr
 
        corr_coefficient, p_value = pearsonr(df_aligned[traffic_information], df_aligned[weather_type])
        
        #plot traffic weather data
        fig1 = px.bar(traffic_plot_data,text=traffic_plot_data.index.weekday.astype('str'))#,color_discrete_sequence=['green','red','blue','goldenrod','magenta','orange','brown'])#,color=plot_data.index.weekday.astype('str'))      
        fig1.update_layout(title_x=0.5,barmode='overlay',showlegend=False)
        fig1.update_traces(opacity=0.5,width=__define_bar_width(frequency_traffic),marker_color=c)
        fig2 = px.scatter(weather_plot_data,color_discrete_sequence=['green'])                        
        fig2.update_traces(yaxis='y2',opacity=0.5,mode='lines+markers',marker=dict(size=weather_marker_size))
        #combine barplot and line plot
        subfig = make_subplots(specs=[[{"secondary_y": True}]])
        subfig.add_traces(fig2.data + fig1.data)
        subfig.update_xaxes({'range': (pd.to_datetime(start_date), pd.to_datetime(end_date))})
        subfig.update_layout(yaxis_title=('{} {}').format(statistic_traffic,traffic_information))
        subfig.update_layout(yaxis2_title = weather_type)
        subfig.update_layout(title_x=0.5,title_text=('{} traffic {} on {} between {} and {} vs {} in {} - corr = {} ({})').format(statistic_traffic,traffic_information,inputs['plot_title_road'],pd.to_datetime(start_date).date(),pd.to_datetime(end_date).date(),weather_type,inputs['city'],round(corr_coefficient,2),round(p_value,4)))        
                
        #plot traffic per road data
        if clickdata != None:
            date1,date2 = __define_datetime_range(clickdata,frequency_traffic,pd)  
            print(date1)
            print(date2)
            plot_data_fig3 = queried_traffic_data.loc[date1:date2]
        else:
            date1 = start_date
            date2 = end_date
            plot_data_fig3 = queried_traffic_data
        fig3 = px.bar(plot_data_fig3.groupby('Road')[traffic_information].agg(statistic_traffic).sort_values(ascending=False))
        fig3.update_layout(title_x=0.5,title_text=('{} traffic {} on {} between {} and {}').format(statistic_traffic,traffic_information,inputs['plot_title_road'],date1,date2))
        fig3.update_layout(yaxis_title=('{} {}').format(statistic_traffic,traffic_information))
        
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
        
        #Outputs
        # data_to_store = {'queried_traffic_data':queried_data['traffic'].to_dict(),'queried_weather_data':queried_data['weather'].to_dict(),'inputs':inputs,'all_queries':all_queries}
        # data_to_store = {'inputs':inputs,'all_queries':all_queries}

        nr_of_traffics_included = str(queried_traffic_data.shape[0])
        total_pandas_query_output = 'datac.query("' + all_queries['pandas_traffic']+ '")' + '.loc["'+pd.to_datetime(start_date).strftime('%Y-%m-%d').replace('-0','-')+'":"'+pd.to_datetime(end_date).strftime('%Y-%m-%d').replace('-0','-')+'"]'
        return subfig,nr_of_traffics_included,total_pandas_query_output,all_queries['API_traffic'],fig3,{"display": "none"}#,heatmap
    
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
        if month == 'All' or year=='All': #This needs to be improved, but don't know how yet.
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
        
def __combine_all_queries(inputs,traffic_table_name,traffic_columns,weather_table_name,weather_columns,pd):
    start_date = pd.to_datetime(inputs['start_date'])
    end_date = pd.to_datetime(inputs['end_date'])
    from datetime import timedelta
    
    #Pandas query
    periods_total = __period_select(inputs['period'])
    period_query = ('index.dt.hour.isin({})').format(periods_total)
    weekday_query = ("index.dt.weekday.astype('str').isin({})").format(inputs['weekday'])
    root_cause_query = ('Oorzaak_4.isin({})').format(inputs['rootcause'])
    road_query = ('Road in {}').format(inputs['road'])
    city_query = ('city== "{}"').format(inputs['city'])
    
    total_pandas_traffic_query = period_query + ' & ' + weekday_query + ' & ' + root_cause_query + ' & ' + road_query #+ ' & ' + excluded_query 
    total_pandas_weather_query = weekday_query + ' & ' + period_query + ' & ' + city_query

    #API query
    period_filter = '&hours=' + (', '.join(map(str, periods_total)))
    road_filter = '&"Road"=' + (', '.join(map(str, inputs['road'])))
    weekday_filter = '&weekdays=' + (', '.join(map(str, inputs['weekday'])))
    start_date_filter ='&start_date=' + start_date.strftime('%Y-%m-%d')#.replace('-0','-')
    end_date_filter = '&end_date=' + (end_date+timedelta(days=1)).strftime('%Y-%m-%d')#.replace('-0','-')
    rootcause_filter = '&"Oorzaak_4"=' + (', '.join(map(str, inputs['rootcause'])))
    city_filter = '&city=' + inputs['city']
    
    total_API_traffic_query = '?table=' + traffic_table_name + '&' + 'columns=' + traffic_columns + '&' + 'datecolumn="DateTimeStart"' + start_date_filter + end_date_filter + period_filter + road_filter + weekday_filter + rootcause_filter
    total_API_weather_query = '?table=' + weather_table_name + '&' + 'columns=' + weather_columns + '&' + 'datecolumn=date' + start_date_filter + end_date_filter + period_filter + city_filter + weekday_filter
    print(total_API_traffic_query)
    print(total_API_weather_query)
    all_queries = {'pandas_traffic':total_pandas_traffic_query,'API_traffic':total_API_traffic_query,'pandas_weather':total_pandas_weather_query,'API_weather':total_API_weather_query}
    return all_queries
    
    
def __prep_inputs(road,city,weekday,period,rootcause,start_date,end_date,datac,api_base,AIweerfile_functions):
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
        
    inputs = {'road':road,'city':city,'weekday':weekday,'period':period,'plot_title_road':plot_title_road,'rootcause':rootcause,'start_date':start_date,'end_date':end_date}
    return    inputs

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

def __load_all_data(datac,weather_data,triggered_id,all_queries,api_base,AIweerfile_functions,pd,current_traffic_data,start_date,end_date,traffic_trigger_id_list,weather_trigger_id_list,traffic_table_name,traffic_columns,weather_table_name,weather_columns,road,city,weekday,period,rootcause):
    
    if triggered_id in traffic_trigger_id_list or triggered_id in weather_trigger_id_list or current_traffic_data is None:
        # inputs = __prep_inputs(road,city,weekday,period,rootcause,start_date,end_date,datac,api_base,AIweerfile_functions)
        # all_queries = __combine_all_queries(inputs,traffic_table_name,traffic_columns,weather_table_name,weather_columns,pd)

        
        # if triggered_id in traffic_trigger_id_list or current_traffic_data is None:
        #     if datac is None:
        #         data = AIweerfile_functions.call_AIWeerFileAPI(api_base,'main',all_queries['API_traffic'])
        #         queried_traffic_data = pd.DataFrame(data['data'],columns=data['columns'])
        #         queried_traffic_data['DateTimeStart'] = pd.to_datetime(queried_traffic_data['DateTimeStart'])
        #         del data
        #     else:
        #         queried_traffic_data = datac.query(all_queries['pandas_traffic']).loc[start_date:end_date]
        # else:
        #     queried_traffic_data = pd.DataFrame(current_traffic_data['queried_traffic_data'])
        #     queried_traffic_data['DateTimeStart'] = pd.to_datetime(queried_traffic_data['DateTimeStart'])
        
        # if triggered_id in weather_trigger_id_list or current_traffic_data is None:
        #     if weather_data is None:
        #         temp_data = AIweerfile_functions.call_AIWeerFileAPI(api_base,'main',all_queries['API_weather'])
        #         queried_weather_data = pd.DataFrame(temp_data['data'],columns=temp_data['columns'])
        #         queried_weather_data['date'] = pd.to_datetime(queried_weather_data['date'])
        #         del temp_data
        #     else:
        #         queried_weather_data = weather_data.query(all_queries['pandas_weather']).loc[start_date:end_date]
        # else:
        #     queried_weather_data = pd.DataFrame(current_traffic_data['queried_weather_data'])
        #     queried_weather_data['date'] = pd.to_datetime(queried_weather_data['date'])
        print('nothing')

    else:                
        # queried_traffic_data = pd.DataFrame(current_traffic_data['queried_traffic_data'])
        # queried_traffic_data['DateTimeStart'] = pd.to_datetime(queried_traffic_data['DateTimeStart'])
        # queried_weather_data = pd.DataFrame(current_traffic_data['queried_weather_data'])
        # queried_weather_data['date'] = pd.to_datetime(queried_weather_data['date'])
        # inputs = current_traffic_data['inputs']
        # all_queries = current_traffic_data['all_queries']
        print('nothing')
    
        
    
    if datac is None:
        data = AIweerfile_functions.call_AIWeerFileAPI(api_base,'main',all_queries['API_traffic'])
        queried_traffic_data = pd.DataFrame(data['data'],columns=data['columns'])
        queried_traffic_data['DateTimeStart'] = pd.to_datetime(queried_traffic_data['DateTimeStart'])
        queried_traffic_data = queried_traffic_data.sort_values('DateTimeStart').set_index('DateTimeStart')
        del data
    else:
        queried_traffic_data = datac.query(all_queries['pandas_traffic']).loc[start_date:end_date]
    
    if weather_data is None:
        temp_data = AIweerfile_functions.call_AIWeerFileAPI(api_base,'main',all_queries['API_weather'])
        queried_weather_data = pd.DataFrame(temp_data['data'],columns=temp_data['columns'])
        queried_weather_data['date'] = pd.to_datetime(queried_weather_data['date'])
        queried_weather_data = queried_weather_data.sort_values('date').set_index('date')
        del temp_data
    else:
        queried_weather_data = weather_data.query(all_queries['pandas_weather']).loc[start_date:end_date]    
    
    
    queried_data = {'traffic':queried_traffic_data,'weather':queried_weather_data}
    
    return queried_data#, inputs, all_queries


def __get_dropdown_options(pd,datac,weather_data,api_base,AIweerfile_functions):
    
    
    #years
    if datac is None:
        unique_years = sorted(AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=trafics&columns=year&datecolumn="DateTimeStart"')) + ['All']
        unique_months = ['All'] + sorted(AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=trafics&columns=month&datecolumn="DateTimeStart"'))
        min_date = pd.to_datetime(AIweerfile_functions.call_AIWeerFileAPI(api_base,'generic',"?query=SELECT MIN(" + '"DateTimeStart") FROM trafics')[0]).round('D')[0]
        max_date = pd.to_datetime(AIweerfile_functions.call_AIWeerFileAPI(api_base,'generic',"?query=SELECT MAX(" + '"DateTimeStart") FROM trafics')[0]).round('D')[0]
        unique_roads = ['All'] + AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=trafics&columns="Road"')
        unique_rootcauses = AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=trafics&columns="Oorzaak_4"')
    else:
        unique_years = ['All'] + sorted(list(datac.index.year.unique()))
        unique_months = ['All'] + sorted(list(datac.index.month.unique()))
        min_date = datac.index.round('D').min()
        max_date = datac.index.round('D').max()
        unique_roads = ['All'] + list(datac.Road.sort_values().unique())
        unique_rootcauses = datac.Oorzaak_4.unique().tolist()
        
    if weather_data is None:
        unique_cities = AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=weather&columns=city')
    else:        
        unique_cities = weather_data.city.sort_values().unique()
    
    dropdown_options = {'years':{'options':unique_years,'default':unique_years[0]},'months':{'options':unique_months,'default':unique_months[0]},'date_range':[min_date,max_date],'roads':{'options':unique_roads,'default':unique_roads[0]},'cities':{'options':unique_cities,'default':None},'rootcauses':{'options':unique_rootcauses,'default':unique_rootcauses}}
    return dropdown_options


def __populate_dropdown_menu(callback,Output,Input,dropdown_name,dropdown_ids): 
        # callback
        # Output
        # Input
        # dropdown_type: which dropdown menu to update, should match with the dict keys from __get_dropdown_options
        # dropdown_ids: either the dropdown menu id or a list containing the dropdown menu id and the output types to update
        
        if type(dropdown_ids) is list and len(dropdown_ids)>1:
            output1_type = dropdown_ids[1]
            output2_type = dropdown_ids[2] 
            dropdown_id = dropdown_ids[0]
        else:
            output1_type = 'options' 
            output2_type = 'value'
            dropdown_id = dropdown_ids
                       
        @callback(
            Output(dropdown_id,output1_type),
            Output(dropdown_id,output2_type),
            [Input('dropdown_options_store', 'data')]
        )
        def update_dropdown_options(data):
                if data is None:
                    return []  # No data yet
                # Create options for dropdown from the stored data
                
                if type(dropdown_ids) is list and len(dropdown_ids)>1: #daterange
                    output1 = data[dropdown_name][0]
                    output2 = data[dropdown_name][1]
                else: #dropdown or checklist
                    output1 = data[dropdown_name]['options']
                    output2 = data[dropdown_name]['default']
                    
                return output1, output2






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