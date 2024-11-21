from kpi_calculation import kpi_engine
from fastapi import FastAPI, HTTPException
import pandas as pd
from typing import Optional

''''
Start by using 'uvicorn main:app --reload'
'''

with open("smart_app_data.pkl", "rb") as file:
    df = pd.read_pickle(file)

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the KPI Calculation Engine!"}


@app.get("/kpi/{kpiID}/calculate")
async def calculate(
    kpiID: str,
    machineId: Optional[str] = "all_machines",
    machineType: Optional[str] = "any",
    startTime: Optional[str] = "0",
    endTime: Optional[str] = "3"
    ):
    print(f"Received kpiID: {kpiID}, machineId: {machineId}, startTime: {startTime}, endTime: {endTime}")
    methods = {
    name: getattr(kpi_engine, name)
    for name in dir(kpi_engine)
    if callable(getattr(kpi_engine, name)) and not name.startswith("__")
    }
    if kpiID not in methods:
        raise HTTPException(status_code=404, detail=f"Method for calculating '{kpiID}' not found")

    if(kpiID == "dynamic_kpi"):
        result = methods[kpiID](df = df, machine_id = machineId, start_time = startTime, end_time = endTime, machine_type = machineType, kpi_id = kpiID)
        return result    
    result = methods[kpiID](df = df, machine_id = machineId, start_time = startTime, end_time = endTime)
    return {"value": result}

def main_test():
    kpi_engine.dynamic_kpi(df=df, machine_id='all_machines', machine_type='any', start_time='2024-08-27T00:00:00Z', end_time='2024-09-20T00:00:00Z', kpi_id='a')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)