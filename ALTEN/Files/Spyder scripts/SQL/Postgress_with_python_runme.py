# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 11:39:30 2025

@author: rbijman
"""
import pandas as pd
import matplotlib.pyplot as plt

from python_postgress_class import python_postgres as pypg

my_pypg = pypg('database_config.ini','postgresql')

my_pypg.generic_set_query('DROP TABLE IF EXISTS highways')

create_query = ''' CREATE TABLE IF NOT EXISTS highways (
                    road_id SERIAL PRIMARY KEY,
                    road_name varchar(40) NOT NULL,
                    hp_start int,
                    hp_end int) '''

my_pypg.generic_set_query(create_query)

insert_query = 'INSERT INTO highways (road_name,hp_start,hp_end) VALUES (%s,%s,%s)'
insert_vals=[("A1",1,100), ("A2",1,100), ("A4",1,100)]

my_pypg.generic_set_query(insert_query, insert_vals)

update_query = 'UPDATE highways SET hp_start = 7 WHERE road_name = %s'
update_val = ('A2',)

my_pypg.generic_set_query(update_query, update_val)


get_query = 'SELECT * FROM highways'
highways = my_pypg.generic_get_query(get_query)

highways.hp_start.value_counts()
