from src.utils.api import (
    fetch_realtime_api,
    process_query,
)
from pathlib import Path
from uagents import Bureau, Context, Agent
import orjson
from src.messages.temperature import WeatherFields, CurrentTemperature, UserValues
from src.utils.settings import PROJECT_ROOT
temp_monitor = Agent(name="temp", seed="alice recovery phrase")
weather = Agent(name="bob", seed="bob recovery phrase")

MAIN_AGENT_ADDR = "agent1q2x8962wqplupvr45v27sh2njnrjlj7uqnkt6tglvut34pmjscme798lf37"

DATA_PATH = PROJECT_ROOT / 'src' / 'data.json'


async def get_data_from_store(key: str, path: Path):
    try:
        with open(path, 'rb') as d:
            result = orjson.loads(d.read())
            return result['query'][key]
    except (FileNotFoundError, KeyError, TypeError):
        # print('temperature not found in storage')
        return None


@temp_monitor.on_interval(period=1.0, messages={WeatherFields, UserValues})
async def query_request(ctx: Context):
    # ctx.logger.info("Storage: ", temp_monitor._ctx.storage.get("query"))
    # print(temp_monitor._ctx.storage.get("query"))
    query = await get_data_from_store("location", path=DATA_PATH)
    if query and query != "string":
        ctx.logger.info(f"Checking temperature in {query}")
        await ctx.send(weather.address, message=WeatherFields(LOCATION=query))
    # else:
    #     ctx.logger.info('Location not found in storage')


@temp_monitor.on_message(model=CurrentTemperature)
async def query_response(ctx: Context, sender: str, msg: CurrentTemperature):
    d = await get_data_from_store("temperature", path=DATA_PATH)
    print(d, type(d))
    if d:
        message = ""
        if msg.value > d['max']:
            message = "high"
        elif msg.value < d['min']:
            message = "low"
        if message:
            with open(PROJECT_ROOT / 'src' / 'data.json', 'rb') as d:
                result = orjson.loads(d.read())
                result['query']['alert'] = message
                with open(PROJECT_ROOT / 'src' / 'data.json', 'wb') as d:
                    d.write(orjson.dumps(result, option=orjson.OPT_INDENT_2))
            ctx.logger.info(f"message recieved from weather agent: Temperature is too {message}")


@weather.on_message(WeatherFields, replies={CurrentTemperature})
async def fetch_weather_metrics(ctx: Context, sender: str, msg: WeatherFields):
    query = await process_query(msg.LOCATION)
    data = fetch_realtime_api(query)
    temp_val = data['response']['temp_c']
    ctx.logger.info(f"Received temperature limit from Temp monitor: {temp_val} degrees Celsius")
    await ctx.send(sender, message=CurrentTemperature(value=temp_val))


if __name__ == "__main__":
    bureau = Bureau(endpoint="http://127.0.0.1:5060/alert", port=5060)
    bureau.add(weather)
    bureau.add(temp_monitor)
    bureau.run()
