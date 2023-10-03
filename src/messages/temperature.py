from uagents import Agent, Protocol, Model, Context
from src.utils.api import fetch_realtime_api


class TemperatureLimit(Model):
    min_val: int
    max_val: int


class CurrentTemperature(Model):
    current_min: int
    current_max: int


class Alert(Model):
    message: str




