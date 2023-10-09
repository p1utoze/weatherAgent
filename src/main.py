import uvicorn
import multiprocessing
from datetime import datetime
from fastapi import FastAPI, Request, Query, Body, Depends
from uagents import Bureau, Context, Agent, Model
from src.agents.monitor import temp_monitor, weather, get_data_from_store

app = FastAPI(title="Temperature Monitor")
main_agent = Agent(name='main agent', seed='main agent seed')


class UserValues(Model):
    min_value: int
    max_value: int
    location: str


@app.get("/")
async def root(
        q: str = Query(None, include_in_schema=False),
        qtype: str = Query(None, include_in_schema=False),
        ):
    # if q:
    #     query = None
    #     if qtype == 'city':
    #         query = q.capitalize()
    #     elif qtype == 'loc':
    #         query = str(q).strip()
    #     elif qtype == 'ip':
    #         query = q if valid_ip(q) else "auto:ip"

    if temp_monitor.storage.has("query"):
        alert = await get_data_from_store('alert')
        time = await get_data_from_store('timestamp')
        print(alert, time)
        return {"alert": alert, "timestamp": time}
    else:
        return {"alert_set": False}


@app.post("/limit")
async def root(values: UserValues = Body(...)):
    temp_monitor.storage.set("query", {
        'location': values.location,
        'temperature': {
            'min': values.min_value,
            'max': values.max_value,
            'unit': 'celsius'
        },
        'alert': None,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    return {"Min Temperature": values.min_value, "Max Temperature": values.max_value}


def run_bureau():
    bureau = Bureau(endpoint="http://127.0.0.1:5060/alert", port=5050)
    bureau.add(weather)
    bureau.add(temp_monitor)
    bureau.add(main_agent)
    bureau.run()


def run_uvicorn():
    uvicorn.run(app, port=8080)


if __name__ == "__main__":
    # bureau_process = multiprocessing.Process(target=run_bureau)
    # uvicorn_process = multiprocessing.Process(target=run_uvicorn)
    # bureau_process.start()
    # uvicorn_process.start()
    # bureau_process.join()
    # uvicorn_process.join()
    run_bureau()



