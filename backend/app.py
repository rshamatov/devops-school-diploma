#!/usr/bin/python3

from os import stat
import sys
import logging
import requests
import statistics
from os import environ
from datetime import datetime
from flask import Flask, jsonify
from configparser import ConfigParser
from DbConnection import DbConnection
from WeatherAnalysis import get_mean_weather



logging.basicConfig(
    format = '[%(asctime)s] [%(levelname)s] - %(message)s',
    level = logging.DEBUG,
    stream = sys.stdout
)


def get_location(city_name):
    logging.info(f"Selected city - '{city_name}'")
    url = f"https://www.metaweather.com/api/location/search/?query={city_name}"
    logging.debug(f"Requesting URL '{url}'")
    location_response = requests.get(url)
    logging.info(f"Received location {location_response}: {location_response.json()[0]}")
    return location_response.json()[0]

def get_weather(city_name, year, month, day):
    city_woeid = get_location(city_name)['woeid']
    url = f"https://www.metaweather.com/api/location/{city_woeid}/{year}/{month}/{day}"
    logging.debug(f"Requesting URL '{url}'")
    weather_response = requests.get(url)
    logging.debug(f"Received weather: {weather_response.json()}\n")
    return weather_response

def subtract_years(dt, years):
    try:
        dt = dt.replace(year=dt.year-years)
    except ValueError:
        dt = dt.replace(year=dt.year-years, day=dt.day-1)
    return dt


app = Flask(__name__)

# config = ConfigParser()
# config.read('backend.cfg')
DB_USER = environ.get('db_user')        # config['database']['user']
DB_PASS = environ.get('db_pass')        # config['database']['pass']
DB_HOST_IP = environ.get('db_host')     # config['database']['host_ip']
DB_HOST_PORT = environ.get('db_port')   # config['database']['host_port']
DB_NAME = environ.get('db_name')        # config['database']['db_name']

logging.info(
    f"Environment variables: db_host: '{DB_HOST_IP}', " + \
    f"db_port: '{DB_HOST_PORT}', " + \
    f"db_name: '{DB_NAME}', " + \
    f"db_user: '{DB_USER}'")

db_initial = DbConnection(DB_HOST_IP, DB_HOST_PORT, DB_USER, DB_PASS)
db_initial.create_database(DB_NAME)
del db_initial

db = DbConnection(DB_HOST_IP, DB_HOST_PORT, DB_USER, DB_PASS, DB_NAME)


@app.route('/weather/<city>/today/all')
def weather_today_api_return_all(city):
    logging.debug(f"Received request for /weather/{city}/today/all")
    DATE_TODAY =    datetime.today().strftime('%Y-%m-%d')
    YEAR_TODAY =    datetime.today().strftime('%Y')
    MONTH_TODAY =   datetime.today().strftime('%m')
    DAY_TODAY =     datetime.today().strftime('%d')
    logging.info(f"Today is '{DATE_TODAY}'")
    
    weather = get_weather(city, YEAR_TODAY, MONTH_TODAY, DAY_TODAY)
    db.add_dicts_to_weather_table(weather.json())
    result = db.select_all_from_weather_where_date(DATE_TODAY)
    logging.info(
        f"Handled request for /weather/{city}/today - returned list of {len(result)} values")
    return jsonify(result)

@app.route('/weather/<city>/today')
def weather_today_api(city):
    logging.debug(f"Received request for /weather/{city}/today")
    DATE_TODAY =    datetime.today().strftime('%Y-%m-%d')
    YEAR_TODAY =    datetime.today().strftime('%Y')
    MONTH_TODAY =   datetime.today().strftime('%m')
    DAY_TODAY =     datetime.today().strftime('%d')
    logging.info(f"Today is '{DATE_TODAY}'")
    
    weather = get_weather(city, YEAR_TODAY, MONTH_TODAY, DAY_TODAY)
    db.add_dicts_to_weather_table(weather.json())
    result = db.select_main_from_weather_where_date(DATE_TODAY)
    
    logging.info(
        f"Handled request for /weather/{city}/today - returned list of {len(result)} values")
    return jsonify(result)


@app.route('/weather/<city>/today/analysis')
def weather_today_analysis_api(city):
    logging.debug(f"Received request for /weather/{city}/today/analysis")
    DATE_TODAY =    datetime.today().strftime('%Y-%m-%d')
    YEAR_TODAY =    datetime.today().strftime('%Y')
    MONTH_TODAY =   datetime.today().strftime('%m')
    DAY_TODAY =     datetime.today().strftime('%d')
    logging.info(f"Today is '{DATE_TODAY}'")

    weather_mean_template = {
        "applicable_date":          None,
        "the_temp":                 None,
        "wind_direction_compass":   None,
        "wind_speed":               None,
        "air_pressure":             None,
        "humidity":                 None,
        "visibility":               None,
        "predictability":           None
    }

    weather = get_weather(city, YEAR_TODAY, MONTH_TODAY, DAY_TODAY)
    db.add_dicts_to_weather_table(weather.json())
    weather_today = db.select_main_from_weather_where_date(
        DATE_TODAY,
        weather_mean_template.keys())
    
    '''
    the_temp_mean = statistics.mean([w[1] for w in weather_today])
    logging.info(f"debug temp: {[w[1] for w in weather_today]}")
    logging.info(f"Average the_temp for today is {the_temp_mean}")
    '''
    weather_today_mean = get_mean_weather(
        weather_mean_template.keys(), 
        weather_today)
    logging.info(f"Average weather for today is {weather_today_mean}")

    
    DATE_LAST_YEAR =    subtract_years(datetime.today(), 1).strftime('%Y-%m-%d')
    YEAR_LAST_YEAR =    subtract_years(datetime.today(), 1).strftime('%Y')
    MONTH_LAST_YEAR =   subtract_years(datetime.today(), 1).strftime('%m')
    DAY_LAST_YEAR =     subtract_years(datetime.today(), 1).strftime('%d')
    logging.info(f"Date one year ago is '{DATE_LAST_YEAR}'")

    weather = get_weather(city, YEAR_LAST_YEAR, MONTH_LAST_YEAR, DAY_LAST_YEAR)
    db.add_dicts_to_weather_table(weather.json())
    weather_last_year= db.select_main_from_weather_where_date(
        DATE_LAST_YEAR,
        weather_mean_template.keys())
    
    weather_last_year_mean = get_mean_weather(
        weather_mean_template.keys(), 
        weather_last_year)
    logging.info(f"Average weather for last year is {weather_last_year_mean}")


    result = analyze_two_weathers(weather_today_mean, weather_last_year_mean)

    return jsonify(result)


def analyze_two_weathers(this_year, last_year):
    result = {}

    # Temperature
    if this_year["the_temp"] < last_year["the_temp"]:
        r = 'This year is more cold'
    elif this_year["the_temp"] == last_year["the_temp"]:
        r = "The temperature is the same both years"
    else: 
        r = 'This year is more warm'
    result["the_temp"] = [
        r,
        this_year["the_temp"],
        last_year["the_temp"]
        ]

    # Wind Direction
    if this_year["wind_direction_compass"] == last_year["wind_direction_compass"]:
        r = "Wind Direction is the same"
    else:
        r = "Wind Direction is different"
    result["wind_direction_compass"] = [
        r,
        this_year["wind_direction_compass"],
        last_year["wind_direction_compass"]
    ]

    # Wind Speed
    if this_year["wind_speed"] > last_year["wind_speed"]:
        r = "Wind this year is more strong"
    elif this_year["wind_speed"] < last_year["wind_speed"]: 
        r = "Wind last year is more strong"
    else: 
        r = "Wind is the same"
    result["wind_speed"] = [
        r,
        this_year["wind_speed"],
        last_year["wind_speed"]
    ]

    # Air Pressure
    if this_year["air_pressure"] > last_year["air_pressure"]:
        r = "Air Pressure this year is higher"
    elif this_year["air_pressure"] < last_year["air_pressure"]: 
        r = "Air Pressure this year is lower"
    else: 
        r = "Air Pressure is the same"
    result["air_pressure"] = [
        r,
        this_year["air_pressure"],
        last_year["air_pressure"]
    ]

    # Humidity
    if this_year["humidity"] > last_year["humidity"]:
        r = "Humidity this year is higher"
    elif this_year["humidity"] < last_year["humidity"]: 
        r = "Humidity this year is lower"
    else: 
        r = "Humidity is the same"
    result["humidity"] = [
        r,
        this_year["humidity"],
        last_year["humidity"]
    ]

    # Visibility
    if this_year["visibility"] > last_year["visibility"]:
        r = "Visibility this year is higher"
    elif this_year["visibility"] < last_year["visibility"]: 
        r = "Visibility this year is lower"
    else: 
        r = "Visibility is the same"
    result["visibility"] = [
        r,
        this_year["visibility"],
        last_year["visibility"]
    ]

    # Predictability
    if this_year["predictability"] > last_year["predictability"]:
        r = "Predictability this year is higher"
    elif this_year["predictability"] < last_year["predictability"]: 
        r = "Predictability this year is lower"
    else: 
        r = "Predictability is the same"
    result["predictability"] = [
        r,
        this_year["predictability"],
        last_year["predictability"]
    ]

    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0')
