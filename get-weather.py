#!/usr/bin/env python3
# get-weather.py
# Date: 10/02/2022
# Author: Boris Mélène
# 
# Connects to openweathermap.org and pull the weather.
# Version-controlled with GIT
#

### Modules

import argparse, json, sys, time
from configparser import ConfigParser
from urllib import request,parse,error
from pprint import pp

import style

### Variables

BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

outputfile = "/home/mln/Temp/weather_dump.csv"

# Weather Condition Codes
# https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
THUNDERSTORM = range(200, 300)
DRIZZLE = range(300, 400)
RAIN = range(500, 600)
SNOW = range(600, 700)
ATMOSPHERE = range(700, 800)
CLEAR = range(800, 801)
CLOUDY = range(801, 900)

### Functions

def _get_api_key()->str:

    """ Fetch the API key from your configuration file. """
    config = ConfigParser()
    config.read("secrets.ini")

    return config["openweather"]["api_key"]

def read_user_cli_args():

    """Handles the CLI user interactions.
    Returns:
        argparse.Namespace: Populated namespace object

    """

    parser = argparse.ArgumentParser(description="Gets weather and temperature information for a city")
    parser.add_argument(
        "city", 
        nargs="*", # Uses "*" instead of "+" to allow a default value.
        type=str,
        default=["Broxburn"], # nargs implies a list
        help="City name"
    )
    parser.add_argument(
        "-i",
        "--imperial",
        action="store_true",
        help="Display the temperature in imperial units",
    )
    parser.add_argument(
        "-f",
        "--full",
        action="store_true",
        help="Display all data",
    )
    parser.add_argument(
        "-x",
        "--csv",
        action="store_true",
        help="Dump into a CSV file",
    )

    return parser.parse_args()

def build_weather_query(city_input:list, imperial:bool=False)->str:

    """Builds the URL for an API request to OpenWeather's weather API.
    Args:
        city_input (List[str]): Name of a city as collected by argparse
        imperial (bool): Whether or not to use imperial units for temperature

    Returns:
        str: URL formatted for a call to OpenWeather's city name endpoint
    """

    api_key = _get_api_key()
    city_name = " ".join(city_input)
    units = "imperial" if imperial else "metric"
    params = {'q' : city_name, 'units' : units, 'appid' : api_key}
    querystring = parse.urlencode(params) # safe='+' means the + is not encoded in the URL.
    url = BASE_URL + '?' + querystring

    return url

def get_weather_data(query_url:str)->dict:

    """Makes an API request to a URL and returns the data as a Python object.
    Args:
        query_url (str): URL formatted for OpenWeather's city name endpoint
    Returns:
        dict: Weather information for a specific city
    """
    
    try:
        response = request.urlopen(query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401:  # 401 - Unauthorized
            sys.exit("Access denied. Check your API key.")
        elif http_error.code == 404:  # 404 - Not Found
            sys.exit("Can't find weather data for this city.")
        else:
            sys.exit(f"Something went wrong... ({http_error.code})")

    data = response.read()

    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Couldn't read the server response.")

def display_weather_info(weather_data:dict, imperial:bool=False):

    """Prints formatted weather information about a city.
    Args:
        weather_data (dict): API response from OpenWeather by city name
        imperial (bool): Whether or not to use imperial units for temperature
    More information at https://openweathermap.org/current#name
    """

    city = weather_data["name"]
    country = weather_data["sys"]["country"]
    weather_id = weather_data["weather"][0]["id"]
    weather_description = weather_data["weather"][0]["description"]
    temperature = weather_data["main"]["temp"]
    feels_like = weather_data["main"]["feels_like"]
    pressure = weather_data["main"]["pressure"]
    heure = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(weather_data['dt']))

    print(f"{city} ({country}) weather:", end=" ")
    
    # Weather description
    if weather_id in THUNDERSTORM:
        style.change_color(style.RED)
    elif weather_id in DRIZZLE:
        style.change_color(style.REVERSE)
    elif weather_id in RAIN:
        style.change_color(style.REVERSE)
    elif weather_id in SNOW:
        style.change_color(style.WHITE)
    elif weather_id in ATMOSPHERE:
        style.change_color(style.YELLOW)
    elif weather_id in CLEAR:
        style.change_color(style.BLUE)
    elif weather_id in CLOUDY:
        style.change_color(style.RESET)
    else:  # In case the API adds new weather codes
        style.change_color(style.RESET)
    print(f"\t{weather_description.capitalize()}")
    style.change_color(style.RESET)

    print(f"Temperature: {temperature}°{'F' if imperial else 'C'}")
    print(f"Feels like: {feels_like}°{'F' if imperial else 'C'}")
    print(f"Pressure: {pressure} HPa")
    print(f"Time: {heure}")

def csv_dump(csvfile:str):
    temperature = str(weather_data["main"]["temp"])
    pressure = str(weather_data["main"]["pressure"])
    heure = time.strftime('%H:%M:%S', time.localtime(weather_data['dt']))
    date = time.strftime('%Y-%m-%d', time.localtime(weather_data['dt']))
    with open(csvfile, 'a', newline='') as CSV:
        CSV.write(temperature + "," + pressure + "," + date + "," + heure + "\n")

### Main

if __name__ == "__main__":
    user_args = read_user_cli_args()
    query_url = build_weather_query(user_args.city, user_args.imperial)
    weather_data = get_weather_data(query_url)
    if user_args.full:
        pp(weather_data)
    elif user_args.csv:
        csv_dump(outputfile)
    else:
        display_weather_info(weather_data, user_args.imperial)
