README AIWeerFile

The main application that was developed is the so-called AIweerfiledashboard. This dashboard can be used as a tool to search for potential correlations between traffics and the actual weather at the moment of the traffic.

The dashboard is hosted on a local host: http://127.0.0.1:8050/ and can be initiated by running 'python AIweerfiledashboard.py' from the command line. All data to be visualized is taken from the internet using either an API or by reading directly from csv urls. The processed can be stored in two ways, as a pandas dataframe in pickle format, which can directly be read into memory as pandas dataframe, or into an PostgreSQL database. To read the data from the PostgreSQL database I developed a RESTFULL Flask API (api_to_sql_database.py). On initialization of the dashboard the user can choose how to load the data; from the locally hosted PostgreSQL database (default) or from the locally stored pickle files (by appending the system argument '1' to the function call ('python AIweerfiledashboard [1]') on the command line. Initializing of the pickle files and the Flask API will be discussed below.

All helperfunctions for the dashboard/API web requests and API local requests are stored in utilities scripts (AIweerfile_functions, api_utils.py) and are introduced below as well. 

Filestructure:

..\AIWeerfiledashboard\
	AIweerfiledashboard.py
  	Subfunctions\
		app_layout.py
		callbacks.py
		AIweerfile_functions.py
	api\
		api_to_sql_database.py
		api_utils.py
..\SQL\
	python_posgress_class.py
..\ProcessedData\
	datac
	weather_data
..\database_config.ini


Order of application:
0) Make a PostgreSQL database and update the database_config.ini file with your settings: 
1) Populate PostgreSQL database and/or picles files
2) Launch Flask Restfull api to obtain data from PostrgreSQL: python ..\AIweerfiledashboard\api\api_to_sql_database.py
3) Launch AIweerfiledashboard


Code summary:

AIweerfiledashboard.py

The main file that initializes the dashboard and renders all the interactions on the dashboard. The dashboard is build using Dash and consists of a frontend part (app_layout.py) and a backend part (callbacks.py) which are developed as two separate functions to separate the front-end and back-end as much as possible. Both app_layout and callbacks have a 'main()' memberfunctions that serve as initializer.


app_layout.py

In the main() of app_layout.py the developer can switch on/off dashboard tabs to be visualized by calling the subsequent memberfunctions which are defined below the main() member function. Each tab is defined as a member function of the app_layout (likewise in the callbacks function, as explained below). Currently only Update AIWeerFile and update_output are up and running. Of which AIWeerFile is most up to date. For this tab, the dependency of app_layout on the actual data (i.e. dropdown options/radiobuttons) has been transferred to the backend counterpart (callbacks.py). The dropdowns/radiobuttons that are data dependend are left empty on initializiation and only filled when running the respective callbacks (callbacks.py). The same behaviour still needs to be made for the other tabs (i.e. update_output, traffic, heatmap and weather), if the will be made opearble at some point). Nevertheless, also the old behavior in which the data dependency is still inside the app_layout.py function still works for those tabs. De dropdowns/radiobuttons that are independend of the data (e.g. select_traffic_information_type, select_traffic_statistic, select_weather_type) are filled with the respective options directly on instantiation of the layout.


callbacks.py

In the main() of callbacks.py the developer can likewise as in app_layout.py switch on/off dashboard tab callbacks, by calling the subsequent memberfunctions which are defined below the main() member function. Before calling the respective callbacks, the first member function to be executed in the main() is get_dropdown_options which is a callback that checks if the  dropdownoptions are already retrieved from the data and stored. If not, it will be retrieved and stored. In each tab member function the stored dropdown options can be assesed from the store.
For each dashboard tab a memberfunction existst which does (or in the futures should do) the following actions (except for the 'update data' tab, which has a different behavior): 
1) Populate dropdown menus --> reads the data from the store and populates the datadependend dropdown/radiobutton options
2) Populate the date_range --> checks the year/month selected and populates the date range accordingly
3) Build the query --> based on all the selected dropdown/radiobutton settings
4) apply the query --> to either the SQL database (using the API) or to the pandas dataframe from pickles directly
5) update the plots

The 'update data' tab was added to have the ability to update the SQL database and/or pickels files with new data from the dashboard. The data initialization functionality as described elsewhere in this readme is reused on this tab. Data update could also be done from the respective initialization scripts, the 'update data' tab is just a front end.


AIweerfile_functions.py

Utillities for AIweerfile project
#public functions
call_AIweerFileAPI --> wrapper that requests that output from the api call to the locally hosted api_to_sql_database.py
collect_and_clean_AIweerfiledata --> collects and cleans the traffic and weather data files and stores them in pandas dataframes (datac and weather_per_city)
update_sql_database --> wrapper that converts a pandas dataframe to an SQL database (details defined in the database_config.ini)
update_pickle_with_sql_database_data --> queries all data from PostgreSQL database, converts to pandas dataframe and stores into pickle file
getHPrange --> helper function to get all hectometerpaaltjes between begin and end of the reported traffic
#private functions
__get_lat_lon_per_city --> collects all available trajectory cities in the datac database and returns for each of those cities the corresponding lateral and longitudinal coordinates and stores them in a pandas dataframe together with the citynames. To be used for the weather API call
__get_lat_lon --> returns the lateral/longitudinal coordinates of per each city by calling the geocoding_api.open-meteo.com
__get_weather_per_city --> wrapper around get_weater_from_api to cache the api connection and store the output in right format and 
__get_weather_from_api --> returns for each city (lat/lon coordinate combination) the corresponding weather for a set of requested weathertypes (one API call to archive-api.open-meteo.com)
__cache_temp_data --> cache the api connection
__import_python_sql_class --> import the python sql class from another directory in the folder structure 


api_to_sql_database.py

Flask Restfull API to request specific data from PostgreSQL database, currently with tree modes: 1) get_data 2) get_unique 3) get_generic


api_utils.py

utillities for api_to_sql_database
#public functions
set_up_db_connection --> wrapper to setup connection to the PostgreSQL database
column_query --> selects certain columns from database
all_filters_query --> makes query to filter based on value from certain column
date_time_convertor --> to convert datetime object to isoformat
#private functions
__date_time_query --> to query a specific time range from database


python_postgress_class.py

class that can be used to connect to sql database and query from sql database, only the database connection is used currently, the querying is done using the api.


database_config.ini

config file that contains connection information to connect to the SQL databases, currently only PostgreSQL database, but can be extended with other databases as well using tags




