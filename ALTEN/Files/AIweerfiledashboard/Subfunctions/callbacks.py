# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 14:16:27 2025

@author: rbijman
"""

import pandas as pd
import plotly.express as px
from dash import Input, Output, callback
import plotly.graph_objects as go
from scipy.stats import pearsonr
from Subfunctions import AIweerfile_functions



def main(weather_data,traffic_data,working_dir,api_base):
    update_data(working_dir)
    traffic(traffic_data,working_dir,api_base)
    AIWeerFile(weather_data,traffic_data,working_dir,api_base)
    weather(weather_data,traffic_data,api_base)

# Callback to query the data once on app load and store it
def get_dropdown_options(input_data,api_base,tab_name):
    @callback(
        Output('dropdown_options_store_{}'.format(tab_name), 'data'),
        [Input('dropdown_options_store_{}'.format(tab_name), 'data')]
    )
    def load_dropdown_options_on_app_load(dropdown_options):
        if dropdown_options is None:
            dropdown_options = __get_dropdown_options(input_data,api_base)    
        return dropdown_options


def update_data(working_dir):
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
            traffic_data, lat_lon_df, weather_per_city = AIweerfile_functions.collect_and_clean_AIweerfiledata(start_date,end_date,ampm_border,shortlong_border)  
            if btn1>0:
                sql_table_to_update = 'trafics'
                print_message = 'SQL traffic table updated'
                data_to_update = traffic_data
                AIweerfile_functions.update_sql_database(working_dir,data_to_update,sql_table_to_update)
            elif btn2>0:
                sql_table_to_update = 'weather'
                print_message = 'SQL weather table updated'
                data_to_update = weather_per_city
                AIweerfile_functions.update_sql_database(working_dir,data_to_update,sql_table_to_update)
            print(print_message)

        
        #update pickle with sql database contents
        if btn3>0:
            traffic_data_file_path = working_dir + r"\ProcessedData\traffic_data"
            AIweerfile_functions.update_pickle_with_sql_database_data(working_dir,traffic_data_file_path,'trafics')
            weather_per_city_path = working_dir + r"\ProcessedData\weather_data"
            AIweerfile_functions.update_pickle_with_sql_database_data(working_dir,weather_per_city_path,'weather')
            print_message('pickles updated')
            
        return print_message
    return

def traffic(traffic_data,working_dir,api_base):
    tab_name = 'traffic'
    input_data = {'traffic':traffic_data,'weather':None}
    get_dropdown_options(input_data,api_base,tab_name)
    dropdown_menus_to_populate = {'roads':'road_select_'+tab_name,'years':'year_select_'+tab_name,'months':'month_select_'+tab_name,'date_range':['date_range_'+tab_name,'min_date_allowed','max_date_allowed']}
    for dropdown_type, dropdown_id in dropdown_menus_to_populate.items():
            __populate_dropdown_menu(dropdown_type,dropdown_id,tab_name)
    __select_dates(('date_range_{}').format(tab_name),('month_select_{}').format(tab_name),('year_select_{}').format(tab_name),input_data['traffic'],api_base)

    @callback(
        Output(('graph_{}1').format(tab_name),'figure'), 
        Output(('graph_{}2').format(tab_name),'figure'),
        Input(('date_range_{}').format(tab_name),'start_date'),
        Input(('date_range_{}').format(tab_name),'end_date'),
        Input(('road_select_{}').format(tab_name),'value'),
        Input(('split_by_{}').format(tab_name),'value'),
        Input(('excluded_traffics_{}').format(tab_name),'value'),
        Input(('load_data_{}').format(tab_name),'n_clicks')
        )
    def update_output(start_date,end_date,road,split_by,excluded,load_data):
        if split_by=='no_split':
            split_by=None
            
        if load_data:    
            input_dict = {'road':road,'split_by':split_by,'date_range':(start_date,end_date)}
            prepped_inputs = __prep_inputs(input_data['traffic'],api_base,input_dict)
            
            traffic_settings = {}
            traffic_settings['table_name'] = 'trafics'
            traffic_settings['columns'] =  ' , '.join(['"DateTimeStart"','"Road"','"direction"','"shortlong"','"ampm"','"weekday"'])     
            traffic_settings['active_filters'] = ['road']
            traffic_settings['date_column'] = "DateTimeStart"
            # time.sleep(1)
            all_queries = {}
            all_queries['traffic'] = __combine_all_queries(prepped_inputs,traffic_settings['table_name'],traffic_settings['columns'],traffic_settings['date_column'],traffic_settings['active_filters'])
            
            queried_traffic_data = __load_all_data(input_data,'traffic',all_queries,api_base,start_date,end_date)     
    
            #resample the data
            traffic_plot_data = queried_traffic_data
            print(traffic_plot_data.shape)
        
                
            fig2 = px.histogram(traffic_plot_data.loc[start_date:end_date].reset_index(),x=traffic_settings['date_column'],color=split_by,
                               nbins=1000,
                               labels='counts',
                               title=('Number of Traffics on {} between {} and {}').format(road,pd.to_datetime(start_date).date(),pd.to_datetime(end_date).date())
                               )
            fig2.update_layout(title_x=0.5,barmode='overlay',showlegend=True)
            fig2.update_traces(opacity=0.5)
            if len(fig2['data'])==1:
                fig2['data'][0]['showlegend']=True
                fig2['data'][0]['name']='Number of Traffics'
                
            # fig1 = __plot_files_HMpaal(traffic_data,start_date,end_date,split_by,road,excluded,working_dir)  
            # fig2 = __plot_files_date(traffic_data,start_date,end_date,split_by,road)
            fig1 = fig2
        else:            
            fig1 = go.Figure()
            fig2 = go.Figure()
        
        return fig1, fig2
    return
            
def weather(weather_data,traffic_data,api_base):
    tab_name = 'weather_and_traffic'
    input_data = {'traffic':traffic_data,'weather':weather_data}
    get_dropdown_options(input_data,api_base,tab_name)
    dropdown_menus_to_populate = {'roads':'road_select_'+tab_name,'years':'year_select_'+tab_name,'months':'month_select_'+tab_name,'date_range':['date_range_'+tab_name,'min_date_allowed','max_date_allowed'],'cities':'city_select_' + tab_name}
    for dropdown_type, dropdown_id in dropdown_menus_to_populate.items():
            __populate_dropdown_menu(dropdown_type,dropdown_id,tab_name)
    __select_dates(('date_range_{}').format(tab_name),('month_select_{}').format(tab_name),('year_select_{}').format(tab_name),input_data['traffic'],api_base,)

    @callback(
        Output(('graph_{}').format(tab_name),'figure'), 
        Input(('date_range_{}').format(tab_name),'start_date'),
        Input(('date_range_{}').format(tab_name),'end_date'),
        Input(('city_select_{}').format(tab_name),'value'),
        Input(('weather_type_{}').format(tab_name),'value'),
        Input(('road_select_{}').format(tab_name),'value'),
        Input(('split_by_{}').format(tab_name),'value'),
        Input(('load_data_{}').format(tab_name),'n_clicks')
        )
    def update_output(start_date,end_date,city,weather_type,road,split_by,load_data):
        from plotly.subplots import make_subplots
        if split_by=='no_split':
            split_by=None
            
        if load_data:
            
            input_dict = {'road':road,'split_by':split_by,'date_range':(start_date,end_date),'city':city}
            prepped_inputs = __prep_inputs(input_data['traffic'],api_base,input_dict)
            
            traffic_settings = {}
            traffic_settings['table_name'] = 'trafics'
            traffic_settings['columns'] =  ' , '.join(['"DateTimeStart"','"Road"','"direction"','"shortlong"','"ampm"'])      
            traffic_settings['active_filters'] = ['road','period','weekday','rootcause']
            traffic_settings['date_column'] = "DateTimeStart"
            
            weather_settings = {}
            weather_settings['table_name'] = 'weather'
            weather_settings['columns'] = ' , '.join(['date']) + ' , ' + '"' + weather_type + '"'
            weather_settings['active_filters'] = ['weekday','period','city']
            weather_settings['date_column'] = "date"
            
            all_queries = {}
            all_queries['traffic'] = __combine_all_queries(prepped_inputs,traffic_settings['table_name'],traffic_settings['columns'],traffic_settings['date_column'],traffic_settings['active_filters'])
            all_queries['weather'] = __combine_all_queries(prepped_inputs,weather_settings['table_name'],weather_settings['columns'],weather_settings['date_column'],weather_settings['active_filters'])        
            
            queried_traffic_data = __load_all_data(input_data,'traffic',all_queries,api_base,start_date,end_date)     
            queried_weather_data = __load_all_data(input_data,'weather',all_queries,api_base,start_date,end_date)     
            print(queried_traffic_data.shape)
            
            
            fig2 = px.line(queried_weather_data.loc[start_date:end_date],color_discrete_sequence=['green'])                        
            fig2.update_traces(yaxis='y2')
            subfig = make_subplots(specs=[[{"secondary_y": True}]])
            fig1 = __plot_files_date(queried_traffic_data,start_date,end_date,split_by,road)
            subfig.add_traces(fig1.data + fig2.data)   
            subfig.update_layout(title_x=0.5,title_text=('Number of traffic on {} between {} and {} vs {} in {}').format(road,pd.to_datetime(start_date).date(),pd.to_datetime(end_date).date(),weather_type,city)) 
        else:
            subfig = go.Figure()
        return subfig
    
def AIWeerFile(weather_data,traffic_data,working_dir,api_base):
    tab_name = 'further'
    input_data = {'traffic':traffic_data,'weather':weather_data}
    get_dropdown_options(input_data,api_base,tab_name)
    dropdown_menus_to_populate = {'roads':'road_select_'+tab_name,'years':'year_select_'+tab_name,'months':'month_select_'+tab_name, 'date_range':['date_range_'+tab_name,'min_date_allowed','max_date_allowed'],'rootcauses':'rootcause_' + tab_name,'cities':'city_select_' + tab_name}
    for dropdown_type, dropdown_id in dropdown_menus_to_populate.items():
            __populate_dropdown_menu(dropdown_type,dropdown_id,tab_name)
    __select_dates(('date_range_{}').format(tab_name),('month_select_{}').format(tab_name),('year_select_{}').format(tab_name),input_data['traffic'],api_base)
        
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
        Input(('statistic_traffic_{}').format(tab_name),'value'),
        Input(('weekday_{}').format(tab_name),'value'),
        Input(('period_{}').format(tab_name),'value'),
        Input(('frequency_traffic_{}').format(tab_name),'value'),
        Input(('rootcause_{}').format(tab_name),'value'),
        Input(('statistic_weather_{}').format(tab_name),'value'),
        Input(('frequency_weather_{}').format(tab_name),'value'),      
        Input(('weather_marker_size_{}').format(tab_name),'value'),
        Input(("graph_{}").format(tab_name),'clickData'),
        Input(("subtract_weekday_average_{}").format(tab_name),'value')
        )
    def update_output(start_date,end_date,city,weather_type,road,traffic_information,statistic_traffic,weekday,period,frequency_traffic,rootcause,statistic_weather,frequency_weather,weather_marker_size,clickdata,subtract_weekday_average):
        input_dict = {'road':road,'city':city,'weekday':weekday,'period':period,'rootcause':rootcause,'date_range':(start_date,end_date)}
        prepped_inputs = __prep_inputs(input_data['traffic'],api_base,input_dict)
        
        traffic_settings = {}
        traffic_settings['table_name'] = 'trafics'
        traffic_settings['columns'] =  ' , '.join(['"DateTimeStart"','"Road"','"direction"','"shortlong"','"ampm"']) + ' , ' + '"' + traffic_information + '"'        
        traffic_settings['active_filters'] = ['road','period','weekday','rootcause']
        traffic_settings['date_column'] = "DateTimeStart"
        
        weather_settings = {}
        weather_settings['table_name'] = 'weather'
        weather_settings['columns'] = ' , '.join(['date']) + ' , ' + '"' + weather_type + '"'
        weather_settings['active_filters'] = ['weekday','period','city']
        weather_settings['date_column'] = "date"
        
        all_queries = {}
        all_queries['traffic'] = __combine_all_queries(prepped_inputs,traffic_settings['table_name'],traffic_settings['columns'],pd,traffic_settings['date_column'],traffic_settings['active_filters'])
        all_queries['weather'] = __combine_all_queries(prepped_inputs,weather_settings['table_name'],weather_settings['columns'],pd,weather_settings['date_column'],weather_settings['active_filters'])        
        
        queried_traffic_data = __load_all_data(input_data,'traffic',all_queries,api_base,pd,start_date,end_date)     
        queried_weather_data = __load_all_data(input_data,'weather',all_queries,api_base,pd,start_date,end_date)     
        print(queried_traffic_data.shape)

        #resample the data
        traffic_plot_data = queried_traffic_data.reset_index().resample(frequency_traffic,on=traffic_settings['date_column'])[traffic_information].agg(statistic_traffic).dropna()
        traffic_plot_data = __shift_time_index(traffic_plot_data,frequency_traffic).to_frame()
        weather_plot_data = queried_weather_data.reset_index().resample(frequency_weather,on=weather_settings['date_column'])[weather_type].agg(statistic_weather)
        weather_plot_data = __shift_time_index(weather_plot_data,frequency_weather).to_frame().dropna()
        
        if 'on' in subtract_weekday_average:
            traffic_plot_data[traffic_information] = traffic_plot_data[traffic_information] - traffic_plot_data.groupby(traffic_plot_data.index.weekday)[traffic_information].transform('mean')
        
        color_dict = {0:'blue',1:'red',2:'green',3:'orange',4:'black',5:'gold',6:'pink'}
        c = traffic_plot_data.index.weekday.map(color_dict)
        
        # Aligning the series based on their indexes (intersection of dates)
        df_aligned = traffic_plot_data.join(weather_plot_data, how='inner')  # 'inner' will align only common dates
        
        # Calculate the correlation
        if df_aligned.shape[0]>0:
            corr_coefficient, p_value = pearsonr(df_aligned[traffic_information], df_aligned[weather_type])
        else:
            corr_coefficient, p_value = (0,0)
        
        #plot traffic weather data
        from plotly.subplots import make_subplots
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
        subfig.update_layout(title_x=0.5,title_text=('{} traffic {} on {} between {} and {} vs {} in {} - corr = {} ({})').format(statistic_traffic,traffic_information,prepped_inputs['plot_title_road'],pd.to_datetime(start_date).date(),pd.to_datetime(end_date).date(),weather_type,prepped_inputs['city'],round(corr_coefficient,2),round(p_value,4)))        
                
        #plot traffic per road data
        if clickdata != None:
            date1,date2 = __define_datetime_range(clickdata,frequency_traffic,pd)  
            plot_data_fig3 = queried_traffic_data.loc[date1:date2]
        else:
            date1 = start_date
            date2 = end_date
            plot_data_fig3 = queried_traffic_data
        fig3 = px.bar(plot_data_fig3.groupby('Road')[traffic_information].agg(statistic_traffic).sort_values(ascending=False))
        fig3.update_layout(title_x=0.5,title_text=('{} traffic {} on {} between {} and {}').format(statistic_traffic,traffic_information,prepped_inputs['plot_title_road'],date1,date2))
        fig3.update_layout(yaxis_title=('{} {}').format(statistic_traffic,traffic_information))
        
        # #heatmap plotting
        # op_vs_af = pd.crosstab(queried_data.Road,queried_data.direction,queried_data[traffic_information],aggfunc=statistic,dropna=True).fillna(pd.NA)  
        # short_vs_long = pd.crosstab(queried_data.Road,queried_data.shortlong,queried_data[traffic_information],aggfunc=statistic).fillna(pd.NA)  
        # am_vs_pm = pd.crosstab(queried_data.Road,queried_data.ampm,queried_data[traffic_information],aggfunc=statistic).fillna(pd.NA)   
        # # per_weekday = pd.crosstab(queried_data.Road,queried_data.DateTimeStart.sort_values().dt.day_name().apply(lambda x:x[0:3]),traffic_data[traffic_information],aggfunc=statistic)[['Mon','Thu','Wed','Thu','Fri','Sat','Sun']].fillna(pd.NA)  
        # # per_month = pd.crosstab(queried_data.Road,queried_data.DateTimeStart.sort_values().dt.month_name().apply(lambda x: x[0:3]),traffic_data[traffic_information],aggfunc=statistic).fillna(pd.NA)  
        # rainy_vs_dry = pd.crosstab(queried_data.Road,queried_data.rainydry,queried_data[traffic_information],aggfunc=statistic).fillna(pd.NA)
        # temp_cat = pd.crosstab(queried_data.Road,queried_data.temp_cat,queried_data[traffic_information],aggfunc=statistic).fillna(pd.NA)

        # # trafic_per_cat = pd.concat([op_vs_af,short_vs_long,am_vs_pm,per_weekday,per_month,temp_cat,rainy_vs_dry],axis=1)
        # trafic_per_cat = pd.concat([op_vs_af,short_vs_long,am_vs_pm,temp_cat,rainy_vs_dry],axis=1)
        # trafic_per_cat['Total'] = queried_data.groupby('Road')[traffic_information].agg(statistic)   
        # trafic_per_cat_ranked= trafic_per_cat.rank(ascending=False,method='max').sort_values(by='Total')
        # heatmap = px.imshow(trafic_per_cat_ranked.T)
        
        nr_of_traffics_included = str(queried_traffic_data.shape[0])
        total_pandas_query_output = 'traffic_data.query("' + all_queries['traffic']['pandas']+ '")' + '.loc["'+pd.to_datetime(start_date).strftime('%Y-%m-%d').replace('-0','-')+'":"'+pd.to_datetime(end_date).strftime('%Y-%m-%d').replace('-0','-')+'"]'
        return subfig,nr_of_traffics_included,total_pandas_query_output,all_queries['traffic']['API'],fig3,{"display": "none"}#,heatmap
    
    @callback(
        Output("graph_{}".format(tab_name), "clickData"),
        Input("graph_field", "n_clicks")
        )
    def reset_clickData(n_clicks):
        return None
    return

#Helper functions

def __select_dates(date_range_id,month_select_id,year_select_id,traffic_data,api_base):
    @callback(
        Output(date_range_id,'start_date'),
        Output(date_range_id,'end_date'),
        Input(year_select_id,'value'),
        Input(month_select_id,'value')    
        )
    def update_start_date(year,month):
        if month == 'All' or year=='All': #This needs to be improved, but don't know how yet.
            if traffic_data is None:
                start_date = pd.to_datetime(AIweerfile_functions.call_AIWeerFileAPI(api_base,'generic',"?query=SELECT MIN(" + '"DateTimeStart") FROM trafics')[0]).round('D')[0]
                end_date = pd.to_datetime(AIweerfile_functions.call_AIWeerFileAPI(api_base,'generic',"?query=SELECT MAX(" + '"DateTimeStart") FROM trafics')[0]).round('D')[0]
            else:
                start_date = pd.to_datetime(traffic_data.index.min())
                end_date = pd.to_datetime(traffic_data.index.max())
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
    
def __plot_files_HMpaal(traffic_data,start_date,end_date,split_by,road,excluded,working_dir):
    traffic_data['HPrange'] = traffic_data.apply(lambda x: AIweerfile_functions.getHPrange(x['HPstart'],x['HPend']),axis=1)

    
    excluded_query = 'index==index'
    if 'grens' in excluded:
        excluded_query = 'not traject.str.contains("grens")'
    if '>25km' in excluded:
        excluded_query = 'not distance>25'
    
    fig = px.histogram(traffic_data.query(excluded_query).loc[start_date:end_date].query('Road==@road').explode('HPrange'),x='HPrange',color=split_by,
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
    
def __plot_files_date(traffic_data,start_date,end_date,split_by,road):
    fig = px.histogram(traffic_data.loc[start_date:end_date].query('Road==@road').reset_index(),x='DateTimeStart',color=split_by,
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

def __combine_all_queries(inputs,table_name,columns,pd,datecolumn,active_filters):
    from datetime import timedelta
    total_pandas_query = ''
    total_API_query = '?table=' + table_name + '&' + 'columns=' + columns + '&' + 'datecolumn="' + datecolumn + '"'
    for k,v in inputs.items():
        match k:
            case 'road':
                subquery = ('Road in {}').format(inputs['road'])
                subfilter = '&"Road"=' + (', '.join(map(str, inputs['road'])))
            case 'city':
                subquery = ('city== "{}"').format(inputs['city'])
                subfilter = '&city=' + inputs['city']
            case 'weekday':
                subquery = ("index.dt.weekday.astype('str').isin({})").format(inputs['weekday'])
                subfilter = '&weekdays=' + (', '.join(map(str, inputs['weekday'])))
            case 'period':
                periods_total = __period_select(inputs['period'])
                subquery = ('index.dt.hour.isin({})').format(periods_total)
                subfilter = '&hours=' + (', '.join(map(str, periods_total)))
            case 'rootcause':
                subquery = ('Oorzaak_4.isin({})').format(inputs['rootcause'])
                subfilter = '&"Oorzaak_4"=' + (', '.join(map(str, inputs['rootcause'])))
            case 'start_date':
                start_date = pd.to_datetime(inputs['start_date'])
                subquery = ''
                subfilter = '&start_date=' + start_date.strftime('%Y-%m-%d')#.replace('-0','-')
            case 'end_date':
                end_date = pd.to_datetime(inputs['end_date'])
                subquery = None
                subfilter = '&end_date=' + (end_date+timedelta(days=1)).strftime('%Y-%m-%d')#.replace('-0','-')
        if k in active_filters:    
            if subquery is not None:
                if len(total_pandas_query)>0:
                    total_pandas_query += '&'
                total_pandas_query += subquery
            total_API_query += subfilter
    
    print(f'query2:{total_API_query}')
    all_queries = {'pandas':total_pandas_query,'API':total_API_query}
    return all_queries
        
def __prep_inputs(traffic_data,api_base,input_dict):
    inputs = {}
    for k,v in input_dict.items():
        value = v
        match k:
            case 'road':
                if v=='All':
                    if traffic_data is None:
                        value = AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=trafics&columns="Road"')
                    else: 
                        value=list(traffic_data.Road.unique())
                    inputs['plot_title_road']='All roads'
                else:
                    value = [v]
                    inputs['plot_title_road'] = value[0]
            case 'city':
                if 'road' not in inputs:
                    raise KeyError('road needs to be given as input and should be in input_dict before city')
                if v is None:
                    if traffic_data is None:
                        if len(inputs['road'])==1:
                            tuple_road = tuple(inputs['road']+inputs['road'])
                        else:
                            tuple_road = tuple(inputs['road'])
                        value = AIweerfile_functions.call_AIWeerFileAPI(api_base,'generic','?query=SELECT traject_city, COUNT(*) as count FROM trafics WHERE "Road" IN' +f"{tuple_road} GROUP BY traject_city ORDER BY count DESC LIMIT 1")[0][0]
                    else:
                        value = traffic_data.query('Road in @road').traject_city.value_counts().index[0]
            case 'weekday':
                if 'all' in v:
                    value = ['0','1','2','3','4','5','6']
            case 'period':
                if 'all' in v:
                    value = ['0-6','6-10','10-15','15-19','19-24']

            case 'date_range':
                inputs['start_date'] = v[0]
                inputs['end_date'] = v[1]
        inputs[k] = value
    return inputs
    
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

def __load_all_data(input_data,data_type,all_queries,api_base,pd,start_date,end_date):
    match data_type:
        case 'traffic':
            if data_type in all_queries:
                if input_data[data_type] is None:
                    print(f'query used = {all_queries["traffic"]["API"]}')
                    data = AIweerfile_functions.call_AIWeerFileAPI(api_base,'main',all_queries['traffic']['API'])
                    queried_data = pd.DataFrame(data['data'],columns=data['columns'])
                    queried_data['DateTimeStart'] = pd.to_datetime(queried_data['DateTimeStart'])
                    queried_data = queried_data.sort_values('DateTimeStart').set_index('DateTimeStart')
                    del data
                else:
                    queried_data = input_data[data_type].query(all_queries['traffic']['pandas']).loc[start_date:end_date]
            else:
                queried_data = None
        case 'weather':    
            if data_type in all_queries:
                if input_data[data_type] is None:
                    temp_data = AIweerfile_functions.call_AIWeerFileAPI(api_base,'main',all_queries['weather']['API'])
                    queried_data = pd.DataFrame(temp_data['data'],columns=temp_data['columns'])
                    queried_data['date'] = pd.to_datetime(queried_data['date'])
                    queried_data = queried_data.sort_values('date').set_index('date')
                    del temp_data
                else:
                    queried_data = input_data[data_type].query(all_queries['weather']['pandas']).loc[start_date:end_date]    
            else:
                queried_data = None
                    
    return queried_data#, inputs, all_queries

def __get_dropdown_options(input_data,api_base):
    
    #years
    if input_data['traffic'] is None:
        unique_years = sorted(AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=trafics&columns=year&datecolumn="DateTimeStart"')) + ['All']
        unique_months = ['All'] + sorted(AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=trafics&columns=month&datecolumn="DateTimeStart"'))
        min_date = pd.to_datetime(AIweerfile_functions.call_AIWeerFileAPI(api_base,'generic',"?query=SELECT MIN(" + '"DateTimeStart") FROM trafics')[0]).round('D')[0]
        max_date = pd.to_datetime(AIweerfile_functions.call_AIWeerFileAPI(api_base,'generic',"?query=SELECT MAX(" + '"DateTimeStart") FROM trafics')[0]).round('D')[0]
        unique_roads = ['All'] + AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=trafics&columns="Road"')
        unique_rootcauses = AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=trafics&columns="Oorzaak_4"')
    else:
        unique_years = ['All'] + sorted(list(input_data['traffic'].index.year.unique()))
        unique_months = ['All'] + sorted(list(input_data['traffic'].index.month.unique()))
        min_date = input_data['traffic'].index.round('D').min()
        max_date = input_data['traffic'].index.round('D').max()
        unique_roads = ['All'] + list(input_data['traffic'].Road.sort_values().unique())
        unique_rootcauses = input_data['traffic'].Oorzaak_4.unique().tolist()
        
    if input_data['weather'] is None:
        unique_cities = AIweerfile_functions.call_AIWeerFileAPI(api_base,'unique','?table=weather&columns=city')
    else:        
        unique_cities = input_data['weather'].city.sort_values().unique()
    
    dropdown_options = {'years':{'options':unique_years,'default':unique_years[0]},'months':{'options':unique_months,'default':unique_months[0]},'date_range':[min_date,max_date],'roads':{'options':unique_roads,'default':unique_roads[0]},'cities':{'options':unique_cities,'default':None},'rootcauses':{'options':unique_rootcauses,'default':unique_rootcauses}}
    return dropdown_options


def __populate_dropdown_menu(dropdown_name,dropdown_ids,tab_name): 
        # callback
        # Output
        # Input
        # dropdown_name: which dropdown menu to update, should match with the dict keys from __get_dropdown_options
        # dropdown_ids: either the dropdown menu id or a list containing the dropdown menu id and the output types to update
        
        if type(dropdown_ids) is list and len(dropdown_ids)>1:
            output1_type = dropdown_ids[1]
            output2_type = dropdown_ids[2] 
            dropdown_id = dropdown_ids[0]
        else:
            output1_type = 'options' 
            output2_type = 'value'
            dropdown_id = dropdown_ids
            
        if tab_name=='traffic':
            print(dropdown_id)
                       
        @callback(
            Output(dropdown_id,output1_type),
            Output(dropdown_id,output2_type),
            [Input('dropdown_options_store_{}'.format(tab_name), 'data')]
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

# def __plot_on_map(traffic_data,weather_data):
#     import geopandas as gpd
#     url1 = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
#     world = gpd.read_file(url1)[['SOV_A3', 'POP_EST', 'CONTINENT', 'NAME', 'GDP_MD', 'geometry']]
#     world = world.set_index("SOV_A3")
    
#     from plotly.subplots import make_subplots
#     subfig = make_subplots()
    
#     fig1 = world.query('SOV_A3=="NL1"').plot()
#     fig2 = px.scatter(traffic_data.query('Road=="A4"').groupby(by=['lat_middle','lon_middle']).Duration.mean().reset_index(),x='lon_middle',y='lat_middle',c='Duration')
#     cities_of_interest = ['Utrecht','Amsterdam','Rotterdam','Gouda','Eindhoven','Zwolle','Groningen','Maastricht']
#     test = weather_data.query("city in @cities_of_interest")
    
#     subfig.add_traces(fig1,fig2)

#     for idx,city in enumerate(test.city):
#         subfig.add_annotation(text=test.city.iloc[idx], x=test.lon.iloc[idx],y=test.lat.iloc[idx])
#     return subfig

