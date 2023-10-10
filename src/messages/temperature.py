from uagents import Model


class UserValues(Model):
    """
    /limit POST request body parameters
    """
    min_value: int
    max_value: int
    location: str


class CurrentTemperature(Model):
    """
    Message Passing Model from weather agent to temp_monitor agent
    """
    value: float


class WeatherFields(Model):
    """
    Weather API response fields passed from temp_monitor agent to weather agent
    """
    LOCATION: str
