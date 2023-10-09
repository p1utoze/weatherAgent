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
    query = await get_data_from_store("location", path=DATA_PATH)
    if query and query != "string":
        ctx.logger.info(f"Checking temperature in {query}")
        await ctx.send(weather.address, message=WeatherFields(LOCATION=query))
    # else:
    #     ctx.logger.info('Location not found in storage')


@temp_monitor.on_message(model=CurrentTemperature)
async def query_response(ctx: Context, sender: str, msg: CurrentTemperature):
    """
       This function recieves the message from weather Agent through the pydantic Model CurrentTemperature. It then
         checks the temperature value and compares it to the user's set values from the user request.
         If the temperature is too high or too low the message is assigned the value to the 'alert' key in the data.json
        file.
    :param ctx:
    :param sender:
    :param msg:
    :return:
    """
    d = await get_data_from_store("temperature", path=DATA_PATH)
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
                with open(PROJECT_ROOT / 'src' / 'data.json', 'wb') as f:
                    f.write(orjson.dumps(result, option=orjson.OPT_INDENT_2))
            ctx.logger.info(f"message recieved from weather agent: Temperature is too {message}")


@weather.on_message(WeatherFields, replies={CurrentTemperature})
async def fetch_weather_metrics(ctx: Context, sender: str, msg: WeatherFields):
    query = await process_query(msg.LOCATION)
    data = fetch_realtime_api(query)
    temp_val = data['response']['temp_c']
    ctx.logger.info(f"Received temperature limit from Temp monitor: {temp_val} degrees Celsius")
    await ctx.send(sender, message=CurrentTemperature(value=temp_val))


if __name__ == "__main__":
    '''
    This is the main function that runs the agents ONLY. This tests the agents functionality withing the uAgents
    ecosystem under bureau. 
    >>> python -m src.agents.temp_monitor
    '''
    bureau = Bureau(endpoint="http://127.0.0.1:5060/alert", port=5060)
    bureau.add(weather)
    bureau.add(temp_monitor)
    bureau.run()
