from kpi_calculation import kpi_engine
from fastapi import FastAPI, HTTPException
import pandas as pd
from typing import Optional

''''
Start by using 'uvicorn main:app --reload'

Examples of basic queries:
GET http://127.0.0.1:8000/kpi/power_consumption_efficiency/calculate?machineId=all_machines (expected value =~ 357.414,5325)
GET http://127.0.0.1:8000/kpi/availability/calculate?machineId=ast-hnsa8phk2nay (expected value =~ 0,9799)
'''

pd.set_option('display.max_rows', None)

with open("smart_app_data.pkl", "rb") as file:
    df = pd.read_pickle(file)

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the KPI Calculation Engine!"}


@app.get("/kpi/{kpiID}/calculate")
async def calculate(
    kpiID: str,
    machineId: str,
    startTime: str,
    endTime: str
    # startTime: Optional[str] = "0",
    # endTime: Optional[str] = "3"
    ):
    print(f"Received kpiID: {kpiID}, machineId: {machineId}, startTime: {startTime}, endTime: {endTime}")
    methods = {
    name: getattr(kpi_engine, name)
    for name in dir(kpi_engine)
    if callable(getattr(kpi_engine, name)) and not name.startswith("__")
    }
    if kpiID not in methods:
        raise HTTPException(status_code=404, detail=f"Method for calculating '{kpiID}' not found")

    result = methods[kpiID](df = df, machine_id = machineId, start_time = startTime, end_time = endTime)
    return {"value": result}

def main_test():
    kpi_engine.dynamic_kpi(df=df, machine_id='all_machines', machine_type='any', start_time='2024-08-27T00:00:00Z', end_time='2024-09-20T00:00:00Z', kpi_id='a')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
    