import requests
import os
import socket
from dotenv import load_dotenv
from .settings import ENV_PATH

# Load the environment variables or from configured .env file
load_dotenv(ENV_PATH)

_extra_params = ['wind_degree', 'wind_dir', 'pressure_mb', 'pressure_in',
                 'vis_km', 'vis_miles', 'uv', 'gust_mph', 'gust_kph']


def valid_ip(addr):
    """Check for valid IP address.
    :param addr: IP address to be checked.
    """
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

    response = requests.get(
        f"http://api.weatherapi.com/v1/current.json?key={key}&q={query}&aqi=no")
    try:
        return process_realtime_data(response.json(), query=query)
    except Exception as exc:
        print('There was a problem: %s' % exc)


def process_realtime_data(response: dict, query: str = None) -> dict:
    """
    Process the response from the weatherapi.com API.
    The response data is processed and returned in a dictionary based on the query.
    :param response: JSON response from the API.
    :param query: Location query string set by the user.
    :return: dict
    """
    data = {'query': query, 'response': response['location']}
    for key in response['current']:
        data['response'][key] = response['current'][key]
    for unwanted in _extra_params:
        del data['response'][unwanted]
    return data


async def process_query(query: str | tuple[float, float]):
    """
    Process the query string and return the query string in the required format.
    The query accepts the following format types:
    1. city: City name(e.g. Bengaluru)
    2. loc: Decimal Latitude and Longitude co-ordinates (e.g. 12.9716, 77.5946)
    3. ip: IP address (fetched from the request)
    :param query: str | tuple[float, float]
    :return: str ( Formatted query string )
    """
    if query:
        if type == 'city':
            query = query.capitalize()
        elif type == 'loc':
            query = str(query).strip()
        elif type == 'ip':
            query = query if valid_ip(query) else "auto:ip"

        return query


if __name__ == "__main__":
    print(fetch_realtime_api(query='Bengaluru'))
