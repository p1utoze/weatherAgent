import requests
import json
import os
import socket
from dotenv import load_dotenv
from settings import ENV_PATH
load_dotenv(ENV_PATH)

_extra_params = ['wind_degree', 'wind_dir', 'pressure_mb', 'pressure_in',
                 'vis_km', 'vis_miles', 'uv', 'gust_mph', 'gust_kph']

def valid_ip(addr):
    try:
        socket.inet_aton(addr)
        return True
    except socket.error:
        return False


def fetch_realtime_api(city: str = None, ip: str = None, coord: tuple[float, float] = None):
    """
    Fetches weather data from weatherapi.com based on the given parameters as queries.
    Make sure to set the WEATHER_API_KEY environment variable before running this function.
    (You can get the key from https://www.weatherapi.com/)
    :param city: defaults to None
    :type city: str
    :param ip:
    :type ip: str
    :param coord:
    :type coord: tuple[float, float]
    :return: dict
    """
    key = os.getenv("WEATHER_API_KEY")
    if city:
        query = city.capitalize()
    elif coord:
        query = ",".join(map(str, coord))
    else:
        query = ip if valid_ip(ip) else "auto:ip"

    response = requests.get(
        f"http://api.weatherapi.com/v1/current.json?key={key}&q={query}&aqi=no")
    try:
        return process_realtime_data(response.json(), query=query)
    except Exception as exc:
        print('There was a problem: %s' % exc)


def process_realtime_data(response: dict, query: str = None):
    data = {'query': query, 'response': response['location']}
    for key in response['current']:
        data['response'][key] = response['current'][key]
    for unwanted in _extra_params:
        del data['response'][unwanted]
    return data


if __name__ == "__main__":
    print(fetch_realtime_api(city='Bengaluru'))
