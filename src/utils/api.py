import requests
import json
import os
import socket
from dotenv import load_dotenv
from .settings import ENV_PATH
from typing import Any
from src.agents.monitor import temp_monitor

load_dotenv(ENV_PATH)

_extra_params = ['wind_degree', 'wind_dir', 'pressure_mb', 'pressure_in',
                 'vis_km', 'vis_miles', 'uv', 'gust_mph', 'gust_kph']


def valid_ip(addr):
    try:
        socket.inet_aton(addr)
        return True
    except socket.error:
        return False


def fetch_realtime_api(query: str):
    """
    Fetches weather data from weatherapi.com based on the given parameters as queries.
    Make sure to set the WEATHER_API_KEY environment variable before running this function.
    (You can get the key from https://www.weatherapi.com/)
    :param query: The query string to be passed to the API.
    :type query: str
    """
    key = os.getenv("WEATHER_API_KEY")
    if not key:
        raise Exception("WEATHER_API_KEY not set in environment variables.")
    print(query)
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

async def process_query(query: str | tuple[float, float]):
    if query:
        if type == 'city':
            query = query.capitalize()
        elif type == 'loc':
            query = str(query).strip()
        elif type == 'ip':
            query = query if valid_ip(query) else "auto:ip"

        return query


async def get_data_from_store(key: str) -> dict:
    try:
        result = temp_monitor.storage.get("query")
        return result[key]
    except KeyError:
        print('temperature not found in storage')
        return None


if __name__ == "__main__":
    print(fetch_realtime_api(city='Bengaluru'))
