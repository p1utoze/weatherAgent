from src.utils.api import fetch_realtime_api, valid_ip
from enum import Enum
from uagents import Bureau, Context, Agent, Model
from src.messages.temperature import TemperatureLimit, Alert


class WeatherFields(Model):
    LOCATION: str


class CurrentTemperature(Model):
    temp: float

temp_monitor = Agent(name="temp", seed="alice recovery phrase")
weather = Agent(name="bob", seed="bob recovery phrase")

async def process_query(query: str | tuple[float, float]):
    if query:
        if type == 'city':
            query = query.capitalize()
        elif type == 'loc':
            query = str(query).strip()
        elif type == 'ip':
            query = query if valid_ip(query) else "auto:ip"

        return query


@temp_monitor.on_interval(period=12.0, messages=WeatherFields)
async def alice_sends_message(ctx: Context):
    if not ctx.storage.has("temperature"):
        ctx.storage.set("temperature", {'min': 20.0, 'max': 30.0})
    query = 'London'
    ctx.logger.info(f"Checking temperature in {query}")
    await ctx.send(weather.address, message=WeatherFields(LOCATION=query))


@temp_monitor.on_message(model=CurrentTemperature)
async def alice_receives_message(ctx: Context, sender: str, msg: CurrentTemperature):
    d = ctx.storage.get("temperature")
    if d:
        if msg.temp > d['max']:
            message = "Temperature is too high"
        elif msg.temp < d['min']:
            message = "Temperature is too low"
        else:
            message = "Temperature is normal"
        ctx.logger.info(f"message recieved from weather agent: {message}")
    else:
        ctx.logger.info(f"No  preferred temperature range is set by user")


@weather.on_message(WeatherFields, replies={CurrentTemperature})
async def alice_receives_message(ctx: Context, sender: str, msg: WeatherFields):
    query = await process_query(msg.LOCATION)
    data = fetch_realtime_api(query)
    temp_val = data['response']['temp_c']
    ctx.logger.info(f"Received temperature limit from Temp monitor: {temp_val} degrees Celsius")
    await ctx.send(temp_monitor.address, message=CurrentTemperature(temp=temp_val))


if __name__ == "__main__":
    bureau = Bureau(endpoint="http://127.0.0.1:5050/alert", port=5050)
    bureau.add(weather)
    bureau.add(temp_monitor)
    bureau.run()
