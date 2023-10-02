import uvicorn
from uagents import Agent, Model, Context, Bureau
from fastapi import FastAPI, Request, Query
from .utils.api import fetch_realtime_api, valid_ip
temp_monitor = Agent(name='temp monitor')
from uagents import Bureau, Context, Agent, Model

app = FastAPI(title="Temperature Monitor")


@app.on_event("startup")
async def startup_event():
    pass


@app.get("/")
async def root(q: str = Query(None, include_in_schema=False), type: str = Query(None, include_in_schema=False)):
    if q:
        query = None
        if type == 'city':
            query = q.capitalize()
        elif type == 'loc':
            query = str(q).strip()
        elif type == 'ip':
            query = q if valid_ip(q) else "auto:ip"

        print(query)
        data = fetch_realtime_api(query)
        return data

    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, port=5050)


