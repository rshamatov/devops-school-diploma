#!/usr/bin/python3

import sys
import logging
import requests
from datetime import datetime
from os import environ
from flask import Flask, render_template

logging.basicConfig(
    format = '[%(asctime)s] [%(levelname)s] - %(message)s',
    level = logging.DEBUG,
    stream = sys.stdout
)

app = Flask(__name__)
BACKEND_ADDRESS = environ.get('BACKEND_HOST_IP')
BACKEND_PORT = environ.get('BACKEND_HOST_PORT')
WEB_HOST_ADDRESS = f"{BACKEND_ADDRESS}:{BACKEND_PORT}"
logging.info(f"Using Backend address {WEB_HOST_ADDRESS}")
#'backend:5000'

DATE_FORMAT = '%Y-%m-%d'
   
@app.route('/')
def index():
    DATE_TODAY = datetime.today().strftime(DATE_FORMAT)
    return render_template('index.html', date=DATE_TODAY)


@app.route('/weather_test')
def weather():
    DATE_TODAY = datetime.today().strftime(DATE_FORMAT)
    weather_today = [
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
        },
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
        }]
    return render_template('weather.html', date=DATE_TODAY, weather=weather_today)

@app.route('/<city>/weather_today_full')
def weather_today_full(city):

    DATE_TODAY =    datetime.today().strftime(DATE_FORMAT)
    url = f"http://{WEB_HOST_ADDRESS}/weather/{city}/today"
    logging.info(f"Requesting URL '{url}' from backend host '{WEB_HOST_ADDRESS}'")
    weather_today = requests.get(url)
    logging.debug(f"Got weather_today:{ weather_today.json() }")
    return render_template('weather_full.html', date=DATE_TODAY, weather_list=weather_today.json())

@app.route('/<city>/weather_today')
def weather_today(city):
    DATE_TODAY =    datetime.today().strftime(DATE_FORMAT)
    url = f"http://{WEB_HOST_ADDRESS}/weather/{city}/today/analysis"
    logging.info(f"Requesting URL '{url}' from backend host '{WEB_HOST_ADDRESS}'")
    weather_today = requests.get(url)
    logging.debug(f"Got weather_today:{ weather_today.json() }")

    w = []
    for key in weather_today.json().keys():
        w.append([key] + weather_today.json()[key])
    logging.debug(f"Showing {w}")

    return render_template('weather.html', date=DATE_TODAY, weather_analysis=w)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
