from kpi_calculation import kpi_engine
from fastapi import FastAPI, HTTPException
import pandas as pd
import uvicorn
import requests
from pydantic import BaseModel
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from api_auth.api_auth import get_verify_api_key
from fastapi import Depends

env_path = Path(__file__).resolve().parent.parent / ".env"
print(env_path)
load_dotenv(dotenv_path=env_path)

headers = {
    "Content-Type": "application/json",
    "x-kpi-key": "b3ebe1bb-a4e7-41a3-bbcc-6c281136e234"
}
druid_url = "http://router:8888/druid/v2/sql"
query_body = {
        "query": "SELECT * FROM timeseries"
    }
try:
    response = requests.post(druid_url, headers=headers, json=query_body)
    response.raise_for_status()  # Raise an error for bad status codes
    df = response.json()  # Return the JSON response
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
    return
df = pd.DataFrame.from_dict(df, orient='columns')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class KPIRequest(BaseModel):
    KPI_Name: str
    Machine_Name: Optional[str] = "all_machines"
    Machine_Type: Optional[str] = "any"
    Date_Start: Optional[str] = df['time'].min()[:10]
    Date_End: Optional[str] = df['time'].max()[:10]
    Aggregator: Optional[str] = 'sum'
    startPreviousPeriod: Optional[str] = df['time'].min()[:10]
    endPreviousPeriod: Optional[str] = df['time'].max()[:10]

@app.post("/kpi")
async def read_root():
    return {"message": "Welcome to the KPI Calculation Engine!"}

@app.post("/kpi/calculate")
async def calculate(request: KPIRequest, api_key: str = Depends(get_verify_api_key(["gui"]))): # to add or modify the services allowed to access the API, add or remove them from the list in the get_verify_api_key function e.g. get_verify_api_key(["gui", "service1", "service2"])
    ''' print(f"Received request: {request.json()}") '''

    kpiID = request.KPI_Name
    machineId = request.Machine_Name
    machineType = request.Machine_Type
    startPeriod = request.Date_Start
    endPeriod = request.Date_End
    aggregator = request.Aggregator
    unitOfMeasure = 'UoM'
    startPreviousPeriod = request.startPreviousPeriod
    endPreviousPeriod = request.endPreviousPeriod

    # A list of all static KPI method calculation names is compiled for later use
    methods = {
    name: getattr(kpi_engine, name)
    for name in dir(kpi_engine)
    if callable(getattr(kpi_engine, name)) and not name.startswith("__")
    }
    
    if(kpiID == "dynamic_kpi"):
        raise HTTPException(status_code=404, detail=f"'dynamic_kpi' method not directly callable.")

    # If the requested KPI is not in the static methods, call the dynamic KPI method. Otherwise, just call the good old static one
    if kpiID not in methods:
        result = kpi_engine.dynamic_kpi(df = df, machine_id = machineId, start_period = startPeriod, end_period = endPeriod, machine_type = machineType, kpi_id=kpiID)
    else:
        result = methods[kpiID](df = df, machine_id = machineId, machine_type=machineType, start_period = startPeriod, end_period = endPeriod, start_previous_period=startPreviousPeriod, end_previous_period=endPreviousPeriod)
    
    response = {
        "Machine_Name": machineId,
        "KPI_Name": kpiID,
        "Value": result,
        "Measure_Unit": machineType,
        "Date_Start": startPeriod,
        "Date_Finish": endPeriod,
        "Aggregator": aggregator,
        "Forecast": False
    }
    return response

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("KB_HOST"), port=int(os.getenv("KB_PORT", 8000)))