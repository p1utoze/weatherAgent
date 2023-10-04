from uagents import Agent, Protocol, Model, Context
from src.utils.api import fetch_realtime_api


class TemperatureLimit(Model):
    min_val: int
    max_val: int
    scale: str


class CurrentTemperature(Model):
    value: float


class WeatherFields(Model):
    LOCATION: str


class Alert(Model):
    message: str




