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

my_pypg = api_utils.set_up_db_connection(working_dir)

allowed_tables = ['trafics','weather']

@app.get("/AIWeerFile_api/main")
def get_data():
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
            hours = request.args.get('hours', None)
            weekdays = request.args.get('weekdays',None)
            start_date = request.args.get('start_date', None)
            end_date = request.args.get('end_date', None)
            
            query, filter_values = api_utils.all_filters_query(query,all_filters)
            
            # query,filter_values = api_utils.filter_query(query, filters)
            if start_date or end_date or hours or weekdays:
                query,filter_values = api_utils.date_time_query(query,filter_values,start_date,end_date,hours,weekdays,jsonify)
            
            #Apply query on database            
            cursor.execute(query,filter_values)
            
            #Construct the output
            column_names = [desc[0] for desc in cursor.description]
            data = list(cursor)
            result = [dict(zip(column_names,row)) for row in data]
            response = json.dumps({"columns":column_names,"data":result},default = api_utils.datetime_converter,indent=4)
    return response


@app.get("/AIWeerFile_api/unique")
def get_unique():
    with my_pypg.connection.cursor() as cursor:
        
        column = request.args.get('columns',None)
        print(column)
        
        if column in ["year","month"]:
            if column=="year":
                subquery = "DATE_PART('Y'," + '"DateTimeStart")'
            elif column=="month":
                subquery = "DATE_PART('month'," + '"DateTimeStart")'
        else:                
            subquery = column    
        print(subquery)
        cursor.execute(f'SELECT DISTINCT {subquery} FROM trafics')    
        unique_vals = cursor.fetchall()
               
        #Construct output
        all_unique_vals = [unique_val[0] for unique_val in unique_vals]
        return jsonify(all_unique_vals)


if __name__ == '__main__':
    app.run(debug=True)#, use_reloader=False)
