from uagents import Agent, Protocol, Model, Context
from src.utils.api import fetch_realtime_api


class UserValues(Model):
    min_value: int
    max_value: int
    location: str


class CurrentTemperature(Model):
    value: float


class WeatherFields(Model):
    LOCATION: str


class Alert(Model):
    message: str




