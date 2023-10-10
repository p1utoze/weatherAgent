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
weather = Agent(name="weather", seed="bob recovery phrase")

# Set the path to the data.json file
DATA_PATH = PROJECT_ROOT / 'src' / 'data.json'


async def get_data_from_store(key: str, path: Path) -> dict | None:
    """
    This function reads the data.json file and returns the value of the key passed in the function.
    If the File is not found or the key is not found in the file, it returns None.
    The file is read from in binary mode and then decoded using orjson
    :param key: The key to be searched in the data.json file
    :param path: The path to the JSON file
    :return: dict | None
    """
    try:
        with open(path, 'rb') as d:
            result = orjson.loads(d.read())
            return result['query'][key]
    except (FileNotFoundError, KeyError, TypeError):
        # print('temperature not found in storage')
        return None


@temp_monitor.on_interval(period=1.0, messages={WeatherFields})
async def query_request(ctx: Context):
    """
    This function is called every 1 second and sends a message to the weather agent with the location value.
    The function fetches the location value from the JSON file and sends it to through the WeatherFields model.
    :param ctx: The Context object of the uAgent
    :return: None
    """
    query = await get_data_from_store("location", path=DATA_PATH)
    if query and query != "string":
        await ctx.send(weather.address, message=WeatherFields(LOCATION=query))


@temp_monitor.on_message(model=CurrentTemperature)
async def query_response(ctx: Context, msg: CurrentTemperature):
    """
    This function recieves the message from weather Agent through the pydantic model 'CurrentTemperature'.
    It then checks the temperature value and compares it to the user's set values from the user request.
    If the temperature is too high or too low the message is assigned the value to the 'alert' key
    in the JSON file.
    :param ctx: The Context object of the uAgent
    :param msg: The message model response from the weather agent
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
            with open(DATA_PATH, 'rb') as d:
                result = orjson.loads(d.read())
                result['query']['alert'] = message
                with open(DATA_PATH, 'wb') as f:
                    f.write(orjson.dumps(result, option=orjson.OPT_INDENT_2))
            ctx.logger.info(f"message recieved from weather agent: Temperature is too {message}")


@weather.on_message(WeatherFields, replies={CurrentTemperature})
async def fetch_weather_metrics(ctx: Context, sender: str, msg: WeatherFields):
    """
    This function is invoked when the weather agent receives a valid location from the temp_monitor agent.
    It then sends a request to the weather API and fetches the temperature value from the response.
    The weather api is processed using the fetch_realtime_api function implemented in the utils.api file.
    The realtime temperature in degrees Celsius is continuously logged in the console.
    The temperature value is then sent back to the temp_monitor agent through the CurrentTemperature model.
    :param ctx: The Context object of the uAgent
    :param sender: The address of the agent that sent the message
    :param msg: The message model response from the temp_monitor agent
    :return: None
    """
    query = await process_query(msg.LOCATION)
    data = fetch_realtime_api(query)
    temp_val = data['response']['temp_c']
    ctx.logger.info(f"Received temperature limit from Temp monitor: {temp_val} degrees Celsius")
    await ctx.send(sender, message=CurrentTemperature(value=temp_val))


if __name__ == "__main__":
    '''
    This is the main function that runs the agents ONLY. This tests the agents functionality withing the uAgents
    ecosystem under Bureau class.
    '''
    bureau = Bureau(endpoint="http://127.0.0.1:5060/alert", port=5060)
    bureau.add(weather)
    bureau.add(temp_monitor)
    bureau.run()
