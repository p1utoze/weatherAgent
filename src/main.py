import uvicorn
import multiprocessing
import orjson
from src.utils.settings import PROJECT_ROOT
from datetime import datetime
from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from uagents import Bureau
from src.agents.monitor import temp_monitor, weather, get_data_from_store
from src.messages.temperature import UserValues

app = FastAPI(title="Temperature Monitor")

# Allowed origins set to allow all ( * ) for deployment purposes
origins = ['*']

# CORS middleware to allow all origins and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to store the data
JSON_DATA = PROJECT_ROOT / 'src' / 'data.json'


@app.get("/")
async def root():
    """
    This is the main endpoint for the application. It returns the current timestamp and the alert status.
    If the JSON file doesn't exist, it returns None ( No alert set by the user )
    :return: JSON Response
    """
    if JSON_DATA.exists():
        alert = await get_data_from_store('alert', path=JSON_DATA)
        time = await get_data_from_store('timestamp', path=JSON_DATA)
        return {"alert": alert, "timestamp": time}
    else:
        return {"alert": None}


@app.post("/limit")
async def root(values: UserValues = Body(...)):
    """
    This endpoint is used to set the minimum and maximum temperature values and write them to the JSON file.
    The context.storage (or agent.storage) is not used here as the data is not able to be accessed by the other agents
    and between the FastAPI POST methods and the agents functions synchronously and dynamically.
    The data is written to the JSON file with ORJSON and then read by the agents.
    :param values: Pydantic model for the user values receiving POST request body
    :return: 
    """
    with open(JSON_DATA, 'wb') as f:
        f.write(orjson.dumps(
            dict(query={'location': values.location,
                        'temperature': {
                            'min': values.min_value,
                            'max': values.max_value,
                            'unit': 'celsius'
                        },
                        'alert': False,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }),
            option=orjson.OPT_INDENT_2
        ))
    return {
        "Min Temperature": values.min_value, 
        "Max Temperature": values.max_value, 
        "message": "Values set successfully"
        }


def run_bureau():
    """
    This function is used to create a bureau and add the agents to it on Almanac contract endpoint.
    The bureau is then run.
    :return: None
    """
    bureau = Bureau(endpoint="http://0.0.0.0:5050/alert", port=5050)
    bureau.add(weather)
    bureau.add(temp_monitor)
    bureau.run()


def run_uvicorn():
    """
    Starts the FastAPI server on port 8080 and host set to 0.0.0.0 for deployment on Azure Web App services.
    :return: None
    """
    uvicorn.run(app, port=8080, host='0.0.0.0')


if __name__ == "__main__":
    """
    Entry point for the application.
    
    Description:
    This is the main function that starts the bureau and the FastAPI server in separate processes.
    Multiprocessing is required as the bureau is a blocking process and the FastAPI server needs to be running
    simultaneously. This ensures that the bureau is running and the agents are listening for the events 
    when the user sets the alert values and the user requests changes in the JSON file.
    
    >>> python main.py
    """
    bureau_process = multiprocessing.Process(target=run_bureau) # Create a process for the bureau
    uvicorn_process = multiprocessing.Process(target=run_uvicorn) # Create a process for the FastAPI server
    bureau_process.start()
    uvicorn_process.start()
    bureau_process.join()
    uvicorn_process.join()


@app.on_event("shutdown")
async def startup_event():
    """
    This function is used to delete the JSON file when the FastAPI server is shutdown.
    :return: 
    """
    if JSON_DATA.exists(): # Check if the JSON file exists
        JSON_DATA.unlink() # Delete the JSON file
