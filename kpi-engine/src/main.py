from kpi_calculation import kpi_engine
from fastapi import FastAPI, HTTPException
import pandas as pd
import uvicorn
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

env_path = Path(__file__).resolve().parent.parent / ".env"
print(env_path)
load_dotenv(dotenv_path=env_path)

''''
Start by using 'uvicorn main:app --reload'
examples: 
http://127.0.0.1:8000/kpi/quality/calculate 
http://127.0.0.1:8000/kpi/quality/calculate?machineType=Laser%20Cutter
http://127.0.0.1:8000/kpi/quality/calculate?machineType=Laser%20Cutter&endPeriod=2024-10-10
http://127.0.0.1:8000/kpi/yield_to_availability/calculate?machineType=Laser%20Cutter&endPeriod=2024-10-10 (this is a mockup of the dynamic kpi calculation)
'''

with open("smart_app_data.pkl", "rb") as file:
    df = pd.read_pickle(file)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the KPI Calculation Engine!"}


@app.get("/kpi/{kpiID}/calculate")
async def calculate(
    kpiID: str,
    machineId: Optional[str] = "all_machines",
    machineType: Optional[str] = "any",
    startPeriod: Optional[str] = df['time'].min()[:10],
    endPeriod: Optional[str] = df['time'].max()[:10],
    startPreviousPeriod: Optional[str] = "0",
    endPreviousPeriod: Optional[str] = "3"
    ):
    print(f"Received kpiID: {kpiID}, \nmachineId: {machineId}, \nmachineType: {machineType}, \nstartPeriod: {startPeriod}, \nendPeriod: {endPeriod}\n")
    methods = {
    name: getattr(kpi_engine, name)
    for name in dir(kpi_engine)
    if callable(getattr(kpi_engine, name)) and not name.startswith("__")
    }
    
    if(kpiID == "dynamic_kpi"):
        raise HTTPException(status_code=404, detail=f"'dynamic_kpi' method not directly callable.")

    if kpiID not in methods:
        result, formula = kpi_engine.dynamic_kpi(df = df, machine_id = machineId, start_period = startPeriod, end_period = endPeriod, machine_type = machineType, kpi_id=kpiID)
    else:
        result, formula = methods[kpiID](df = df, machine_id = machineId, machine_type=machineType, start_period = startPeriod, end_period = endPeriod, start_previous_period=startPreviousPeriod, end_previous_period=endPreviousPeriod)
    return {    "kpiID": kpiID,
                "formula": formula,
                "machineId": machineId,
                "machineType": machineType,
                "startPeriod": startPeriod,
                "endPeriod": endPeriod,
                "value": result
                }

def main_test():
    kpi_engine.dynamic_kpi(df=df, machine_id='all_machines', machine_type='any', start_period='2024-08-27T00:00:00Z', end_period='2024-09-20T00:00:00Z', kpi_id='a')

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("KB_HOST"), port=int(os.getenv("KB_PORT", 8000)))
    # uvicorn.run(app, host='0.0.0.0', port=8000)
    # main_test()