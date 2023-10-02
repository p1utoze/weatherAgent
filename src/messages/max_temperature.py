from uagents import Agent, Protocol, Model, Context
from src.utils.api import fetch_realtime_api

class Temperature(Model):
    type: str
    value: float

class Alert(Model):
    type: str


min_temp = Protocol(name="cold")


@min_temp.on_message(model=Temperature, replies={Alert})
def min_temp_interval(ctx: Context, msg: Temperature, sender: str):
    if msg.value < 0.0:
        ctx.send(Temperature(type="cold", value=0.0))


