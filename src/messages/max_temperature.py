import requests
import json
import os

response = requests.get("http://api.weatherapi.com/v1/current.json?key=b45b0576a0834094b9380951230110&q=auto:ip")
try:
    print(response.json())
except Exception as exc:
    print('There was a problem: %s' % exc)
