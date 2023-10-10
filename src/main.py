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

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JSON_DATA = PROJECT_ROOT / 'src' / 'data.json'


@app.get("/")
async def root(
        q: str = Query(None, include_in_schema=False),
        qtype: str = Query(None, include_in_schema=False),
):
    if JSON_DATA.exists():
        alert = await get_data_from_store('alert', path=JSON_DATA)
        time = await get_data_from_store('timestamp', path=JSON_DATA)
        return {"alert": alert, "timestamp": time}
    else:
        return {"alert": None}


@app.post("/limit")
async def root(values: UserValues = Body(...)):
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
    return {"Min Temperature": values.min_value, "Max Temperature": values.max_value}


def run_bureau():
    bureau = Bureau(endpoint="http://0.0.0.0:5050/alert", port=5050)
    bureau.add(weather)
    bureau.add(temp_monitor)
    bureau.run()


def run_uvicorn():
    uvicorn.run(app, port=8080, host='0.0.0.0')


if __name__ == "__main__":
    bureau_process = multiprocessing.Process(target=run_bureau)
    uvicorn_process = multiprocessing.Process(target=run_uvicorn)
    bureau_process.start()
    uvicorn_process.start()
    bureau_process.join()
    uvicorn_process.join()
    run_bureau()

@app.on_event("shutdown")
async def startup_event():
    if JSON_DATA.exists():
        JSON_DATA.unlink()
