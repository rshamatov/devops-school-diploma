#!/usr/bin/python3

#from WeatherBackend import WEATHER_TABLE_NAME
import logging
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# psql -h localhost -p 5432 -U user 

'''
example: 
{
    "id":                           4637839049359360,
    "weather_state_name":           "Thunder",
    "weather_state_abbr":           "t",
    "wind_direction_compass":       "NW",
    "created":                      "2021-04-27T18:42:31.374036Z",
    "applicable_date":              "2021-04-27",
    "min_temp":                     1.325,
    "max_temp":                     5.529999999999999,
    "the_temp":                     4.574999999999999,
    "wind_speed":                   4.200518727696917,
    "wind_direction":               303.98986819398806,
    "air_pressure":                 1007.5,
    "humidity":                     83,
    "visibility":                   5.667526644396723,
    "predictability":               80
}
'''

WEATHER_TABLE_NAME = 'weather'
WEATHER_DATE_KEY = 'applicable_date'
WEATHER_TABLE_FORMAT = {
	"id":						'bigint',
	"weather_state_name":		"character(20)",
	"weather_state_abbr":		"character(10)",
	"wind_direction_compass":	"character(3)",
	"created":					"text",
	WEATHER_DATE_KEY:			"text",  # date? 
	"min_temp":					"float",
	"max_temp":					"float",
	"the_temp":					"float",
	"wind_speed":				"float",
	"wind_direction":			"float",
	"air_pressure":				"float",
	"humidity":					"float",
	"visibility":				"float",
	"predictability":			"float"
}
TABLE_PRIMARY_KEY = 'id'


class DbConnection():
    db_name = ''
    tb_format = None

    def __init__(self, host_ip, host_port, username, password, db_name):
        try:
            logging.info(
                f"Creating connection to PostgreSQL database '{db_name}' on host '{host_ip}:{host_port}' using username '{username}'")
            if db_name:
                self.connection = psycopg2.connect(user=username,
                                            password=password,
                                            host=host_ip,
                                            port=host_port,
                                            dbname = db_name)
            else: 
                self.connection = psycopg2.connect(user=username,
                                            password=password,
                                            host=host_ip,
                                            port=host_port)
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.connection.cursor()
            logging.info(f"Connected to database '{db_name}' on host '{host_ip}:{host_port}' using username '{username}'")
            self.create_table(WEATHER_TABLE_NAME, WEATHER_TABLE_FORMAT)
            self.set_primary_key(WEATHER_TABLE_NAME, TABLE_PRIMARY_KEY)
        except (Exception, Error) as error:
            logging.error(f"PostgreSQL exception: '{error}'")

    def create_database(self, db_name):
        try:
            logging.info(f"Creating database {db_name}")
            sql_request = f'CREATE DATABASE {db_name};'
            logging.debug(f"Executing command {sql_request}")
            self.cursor.execute(sql_request)
            logging.info(f"Database {db_name} has been created")
        except psycopg2.errors.DuplicateDatabase as error: 
            logging.info(f"Database '{db_name}' already exists")
        except Exception as error:
            logging.error(f"PostgreSQL exception: '{error}'")

    def create_table(self, tb_name, table_format):
        try:
            logging.info(f"Checking if table '{tb_name}' exists..")
            logging.debug(f"Table format for creating table: {table_format}")
            sql_request = f'CREATE TABLE {tb_name} (\n\t\t'
            sql_request += ',\n\t\t'.join([f"{k}\t{table_format[k]}" for k in table_format.keys()])
            sql_request += ");"
            logging.debug(f"Executing command {sql_request}")
            self.cursor.execute(sql_request)
            logging.info(f"Table {tb_name} has been created")
        except psycopg2.errors.DuplicateTable as error: 
            logging.info(f"Table {tb_name} already exists")
        except Exception as error:
            logging.error(f"PostgreSQL exception: '{error}'")

    def set_tb_format(self, tb_format):
        if type(tb_format):
            return

    def set_primary_key(self, tb_name, primary_key):
        try: 
            logging.info(f"Setting '{primary_key}' as primary key in table '{tb_name}'")
            sql_request = f"ALTER TABLE {tb_name} ADD PRIMARY KEY ({primary_key});"
            logging.debug(f"Executing command {sql_request}")
            self.cursor.execute(sql_request)
            logging.info(f"Primary key in table {tb_name} is '{primary_key}'")
        except psycopg2.errors.InvalidTableDefinition as error:
            logging.info(f"'{primary_key}' is already primary key in table '{tb_name}'") 

    def add_dict_to_weather_table(self, values_dict):
        """
    	"id":						'bigint',
        "weather_state_name":		"character(20)",
        "weather_state_abbr":		"character(10)",
        "wind_direction_compass":	"character(3)",
        "created":					"text",
        "applicable_date":			"text",  # date? 
        "min_temp":					"float",
        "max_temp":					"float",
        "the_temp":					"float",
        "wind_speed":				"float",
        "wind_direction":			"float",
        "air_pressure":				"float",
        "humidity":					"float",
        "visibility":				"float",
        "predictability":			"float"    
        """
        result_values = {}
        result_values['id']                      = values_dict.get('id', 0)
        result_values["weather_state_name"]      = f"""'{values_dict.get("weather_state_name", 'None')}'"""
        result_values["weather_state_abbr"]      = f"""'{values_dict.get("weather_state_abbr", 'None')}'"""
        result_values["wind_direction_compass"]  = f"""'{values_dict.get("wind_direction_compass", 'None')}'"""
        result_values["created"]                 = f"""'{values_dict.get("created", 'None')}'"""
        result_values["applicable_date"]         = f"""'{values_dict.get("applicable_date", 'None')}'"""
        result_values["min_temp"]                = values_dict.get("min_temp", 0)
        result_values["max_temp"]                = values_dict.get("max_temp", 0)
        result_values["the_temp"]                = values_dict.get("the_temp", 0)
        result_values["wind_speed"]              = values_dict.get("wind_speed", 0)
        result_values["wind_direction"]          = values_dict.get("wind_direction", 0)
        result_values["air_pressure"]            = values_dict.get("air_pressure", 0)
        result_values["humidity"]                = values_dict.get("humidity", 0)
        result_values["visibility"]              = values_dict.get("visibility", 0) if values_dict.get("visibility", 0) else 0
        result_values["predictability"]          = values_dict.get("predictability", 0)

        try: 
            logging.debug(f"Inserting into table '{WEATHER_TABLE_NAME}' values '{values_dict}'")
            sql_request = f'INSERT INTO {WEATHER_TABLE_NAME} VALUES(\n\t\t'
            sql_request += ',\n\t\t'.join(str(result_values[k]) for k in result_values.keys()) 
            sql_request += ");"
            logging.debug(f"Executing command {sql_request}")
            self.cursor.execute(sql_request)
            logging.debug(f"Inserted {values_dict} into table {WEATHER_TABLE_NAME}")
            #"INSERT INTO test (num, data) VALUES (%s, %s)"
        except psycopg2.errors.UniqueViolation as error:
            logging.error(f"Tried to insert value to table '{WEATHER_TABLE_NAME}' with the same id: '{values_dict}'")
        except Exception as error:  
            logging.error(f"PostgreSQL exception when tried to insert '{values_dict}': '{error}'")

    def add_dicts_to_weather_table(self, values):
        logging.debug(f"Inserting {len(values)} values into table '{WEATHER_TABLE_NAME}'")
        for value in values: 
            self.add_dict_to_weather_table(value)
        logging.info(f"Inserted {len(values)} values into table '{WEATHER_TABLE_NAME}'")

    def select_all_from_weather_where_date(self, date_str):
        logging.debug(f"Selecting all rows and all columns from table '{WEATHER_TABLE_NAME}' where date is '{date_str}'")
        sql_request = f"""SELECT * FROM {WEATHER_TABLE_NAME} 
                WHERE {WEATHER_DATE_KEY}='{date_str}'"""
        logging.debug(f"Executing command {sql_request}")
        self.cursor.execute(sql_request)
        records = self.cursor.fetchall()
        logging.info(f"Requested {len(records)} records from table 'WEATHER_TABLE_NAME' where date is '{date_str}'")
        return records

    def select_main_from_weather_where_date(self, date_str, columns):
        logging.debug(f"Selecting all rows and main columns from table '{WEATHER_TABLE_NAME}' where date is '{date_str}'")
        sql_request = f"""SELECT {', '.join(columns)} FROM {WEATHER_TABLE_NAME} 
            WHERE {WEATHER_DATE_KEY}='{date_str}'"""
        logging.debug(f"Executing command {sql_request}")
        self.cursor.execute(sql_request)
        records = self.cursor.fetchall()
        logging.info(f"Requested {len(records)} records from table 'WEATHER_TABLE_NAME' where date is '{date_str}'")
        return records

    def __del__(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            logging.info("Connection to database is closed")
