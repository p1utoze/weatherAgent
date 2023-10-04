from src.utils.api import fetch_realtime_api, valid_ip
from uagents import Bureau, Context, Agent, Model, Protocol
from src.messages.temperature import TemperatureLimit, Alert, WeatherFields, CurrentTemperature
temp_monitor = Agent(name="temp", seed="alice recovery phrase")
weather = Agent(name="bob", seed="bob recovery phrase")

MAIN_AGENT_ADDR = "agent1q2x8962wqplupvr45v27sh2njnrjlj7uqnkt6tglvut34pmjscme798lf37"


async def process_query(query: str | tuple[float, float]):
    if query:
        if type == 'city':
            query = query.capitalize()
        elif type == 'loc':
            query = str(query).strip()
        elif type == 'ip':
            query = query if valid_ip(query) else "auto:ip"

        return query


@temp_monitor.on_interval(period=1.0, messages=WeatherFields)
async def query_request(ctx: Context, data: dict = None):
    if data:
        ctx.storage.set("temperature", data)
        query = 'London'
        ctx.logger.info(f"Checking temperature in {query}")
        await ctx.send(weather.address, message=WeatherFields(LOCATION=query))


@temp_monitor.on_message(model=CurrentTemperature)
async def query_response(ctx: Context, sender: str, msg: CurrentTemperature):
    d = ctx.storage.get("temperature")
    if d:
        message = ""
        if msg.value > d['max']:
            message = "high"
        elif msg.value < d['min']:
            message = "low"
        if message:
            ctx.logger.info(f"message recieved from weather agent: Temperature is too {message}")
            await ctx.send(MAIN_AGENT_ADDR, message=Alert(message=message))


@weather.on_message(WeatherFields, replies={CurrentTemperature})
async def fetch_weather_metrics(ctx: Context, sender: str, msg: WeatherFields):
    print("Hi")
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
