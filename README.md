# Weather Agent
A weather agent notifier by a micro AI agent

## GET STARTED 
* Install the necessary libraries
* Create a `.env` file in under /weatherAgent (equivalent to `src` directory level)
* Add the `WEATHER_API_KEY` environment variable. To get your API key, visit [WeatherAPI](https://www.weatherapi.com/) <br>
```
WEATHER_API_KEY=...
```
  NOTE: This project supports the usage of only FREE API.

## Web App
[ThermoGuardian](https://weather-agent-client.vercel.app/) has been developed using ReactJS and deployed on Vercel.  
The web app is a simple UI to interact with the agent. It allows the user to set the temperature threshold and the 
location. The agent will notify the user when the temperature is out of the range-bounds.

![demo](assets/demo.gif)

**The theme of the app responds in real-time.** The background changes based on the weather condition of the location. 
It changes to Night or Day theme based on the timing of the users location

### Teach Stack
1. ReactJS
2. IPv4 and Weather API
3. uAgent supported FastAPI server