# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 11:10:41 2025

@author: rbijman
"""

# https://neon.tech/postgresql/postgresql-python/create-tables

class python_postgres:
    import configparser as configpar
    import psycopg2 as psy
    import pandas.io.sql as psql
    global psy
    global configpar
    global psql
    
    def __init__(self,filename,section):    
        self.__db_info = self.__get_db_info(filename,section)
        self.connect_to_postgres()
        
#Public Members           
    def generic_set_query(self,*args):
        conn = None
        try:
            with psy.connect(**self.__db_info) as conn:
                
                with conn.cursor() as cur:
                    match len(args):            
                        case 1:
                            query=args[0]
                            cur.execute(query)
                            print('Generic query executed')

                        case 2:
                            query = args[0]
                            vals = args[1]
                            if len(vals)>1:
                                for record in vals:
                                    cur.execute(query,record)
                                print('Records created/updated')
                            else:
                                cur.execute(query,vals)
                                print('Record created/updated')
                    
        except Exception as error:
            print(error)
        finally :
            if conn is not None:
              conn.close()       
              
              
    def generic_get_query(self,get_query):
        try: 
            with psy.connect(**self.__db_info) as conn:
                    df = psql.read_sql(get_query,conn)
                    # print('I got for you what you requested')
                    return df
                    
        except Exception as error:
           print(error)
        finally :
           if conn is not None:
             conn.close()                
          
    
    def create_table(self,create_query):
        conn = None
        try:
            with psy.connect(**self.__db_info) as conn:
                
                with conn.cursor() as cur:
                    cur.execute(create_query)
                print('Table created')
                
        except Exception as error:
            print(error)
        finally :
            if conn is not None:
              conn.close()      
              
    def connect_to_postgres(self):
        try:
            with psy.connect(**self.__db_info) as conn:
                print('Connect to the PostgreSQL server.')
                return conn
        except (psy.DatabaseError,Exception) as error:
            print(error)   
                    
#Private members    
    def __get_db_info(self,filename,section):
        # instantiating the parser object
        parser=configpar.ConfigParser()
        parser.read(filename)
    
        db_info={}
        if parser.has_section(section):
             # items() method returns (key,value) tuples
             key_val_tuple = parser.items(section) 
             for item in key_val_tuple:
                 db_info[item[0]]=item[1] # index 0: key & index 1: value
    
        return db_info
     
        

