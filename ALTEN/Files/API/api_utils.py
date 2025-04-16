# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 14:51:29 2025

@author: rbijman
"""

from datetime import datetime


def set_up_db_connection(working_dir):
    def import_python_postgress_class():
        import sys
        sys.path.insert(0,rf'{working_dir}\SQL')
        from python_postgress_class import python_postgres as pypg
        return pypg

    pypg = import_python_postgress_class()

    my_pypg = pypg(rf'{working_dir}\SQL\database_config.ini','postgresql')
    return my_pypg


def column_query(columns,jsonify,table_name):
    if not columns:
        return jsonify({"error":"No columns given"}), 400 
    
    column_list = columns.split(',')
    select_columns = ','.join(column_list)
    query = f"SELECT {select_columns} FROM {table_name} WHERE 1=1"
    return query

def all_filters_query(query,all_filters,start_date,end_date,hours,weekdays,date_column,jsonify):
    filter_values = []
        
    if all_filters:
        for filter_key,filter_value in all_filters.items():
            # query,filter_values = api_utils.filter_query(query, filters)
            if filter_key in ['start_date','hours','weekdays']:
                query,filter_values = __date_time_query(query,filter_values,start_date,end_date,hours,weekdays,date_column,jsonify)            
            elif filter_key in ['"Road"','"Oorzaak_4"','city']:
                value_list = [value.strip() for value in filter_value.split(',')]
                query += f' AND {filter_key} IN %s'
                filter_values.append(tuple(value_list))
    return query, filter_values
    

def datetime_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()
    
#helper functions 
def __date_time_query(query,filter_values,start_date,end_date,hours,weekdays,date_column,jsonify):
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            if start_date < end_date:
                query += f' AND {date_column} BETWEEN %s AND %s'
                filter_values.extend([start_date, end_date])
            else:
                raise ValueError("Start date cannot be after end date")                        
        except ValueError:
            return jsonify({"error": "Invalid date range specified, use format YYYY-MM-DD"}), 400
    
    if hours is not None:
        hours_list = [int(hour) for hour in hours.split(',')]
        query += f' AND EXTRACT(HOUR FROM {date_column}) IN %s'
        filter_values.append(tuple(hours_list))    

    if weekdays is not None:
        weekday_list = [int(weekday)+1 for weekday in weekdays.split(',')]
        weekday_list = [0 if x > 6 else x for x in weekday_list]
        query += "AND DATE_PART('DOW'" + f',{date_column}) IN %s'
        filter_values.append(tuple(weekday_list))
    return query, filter_values