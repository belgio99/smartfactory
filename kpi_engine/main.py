import kpi_calculation
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the KPI Calculation Engine!"}


@app.get("/kpi/{kpiID}/calculate?machineId=xxx&startTime=xxx&endTime=xxx")
async def read_item(kpiID: str, startTime: str, endTime: str, machineId: str = 'all_machines'):
    """
    Path Parameters:
    - `kpiID`: String.

    Query Parameters:
    - `startTime`: Optional query parameter to filter results.

    - `endTime`: Optional query parameter to filter results.
    
    - `machineId`: Optional query parameter to filter results.
    """
    return {"kpiId": kpiID, "startTime": startTime, "endTime": endTime, "machineId": machineId}

def main():
    print("main")

if __name__ == "__main__":
    main()