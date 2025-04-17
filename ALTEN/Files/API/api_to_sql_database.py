# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 15:38:04 2025

@author: rbijman
"""
from flask import Flask, request, jsonify
import json
import api_utils

working_dir = r"C:\Users\rbijman\Documents\GitHub\rgbijmanproductions\ALTEN\Files"


app = Flask(__name__)



allowed_tables = ['trafics','weather']

@app.get("/AIWeerFile_api/main")
def get_data():
    my_pypg = api_utils.set_up_db_connection(working_dir)
    with my_pypg.connection:
        with my_pypg.connection.cursor() as cursor:            
            #Deal with table_names
            table_name = request.args.get('table', None)
            if not table_name or table_name not in allowed_tables:
                return jsonify({"error": "Not allowed or missing tablename"}), 400 
            
            #Deal with columns
            columns = request.args.get('columns',None)
            query = api_utils.column_query(columns,jsonify,table_name)
            
            #Deal with filters
            all_filters = request.args.to_dict()
            date_column = request.args.get('datecolumn',None)
            hours = request.args.get('hours', None)
            weekdays = request.args.get('weekdays',None)
            start_date = request.args.get('start_date', None)
            end_date = request.args.get('end_date', None)
            
            query, filter_values = api_utils.all_filters_query(query,all_filters,start_date,end_date,hours,weekdays,date_column,jsonify)
            
            #Apply query on database            
            cursor.execute(query,filter_values)
            
            #Construct the output
            column_names = [desc[0] for desc in cursor.description]
            data = list(cursor)
            cursor.close()
            del cursor
            result = [dict(zip(column_names,row)) for row in data]
            response = json.dumps({"columns":column_names,"data":result},default = api_utils.datetime_converter,indent=4)
            
            print('new data query:')
            print(query)
        # my_pypg.connection.close() 
        return response


@app.get("/AIWeerFile_api/unique")
def get_unique():
    my_pypg = api_utils.set_up_db_connection(working_dir)
    with my_pypg.connection.cursor() as cursor:
        table = request.args.get('table',None)
        column = request.args.get('columns',None)
        date_column = request.args.get('datecolumn',None)       
        if column in ["year","month"]:
            if column=="year":
                subquery = "DATE_PART('Y'," + f'{date_column})'
            elif column=="month":
                subquery = "DATE_PART('month'," + f'{date_column})'
        else:                
            subquery = column
        
        query = f'SELECT DISTINCT {subquery} FROM {table}'
        cursor.execute(query)    
        unique_vals = cursor.fetchall()
               
        #Construct output
        all_unique_vals = [unique_val[0] for unique_val in unique_vals]
        
        print('new unique query:')
        print(query)
        return jsonify(all_unique_vals)
    
@app.get("/AIWeerFile_api/generic")
def get_generic():
    my_pypg = api_utils.set_up_db_connection(working_dir)
    with my_pypg.connection.cursor() as cursor:
        
        query = request.args.get('query',None)
        
        if query:
            #DO SOME CHECKS FOR THE QUERY HERE TO NOT RUIN THE DATABASE
            cursor.execute(query)
            generic_vals = cursor.fetchall()
            
            print('new generic query:')
            print(query)
        return jsonify(generic_vals)
            


if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
