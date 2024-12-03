import f_CharacterizeKPI
import f_forecasting
import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models_path = 'models/'

#http://localhost:8000/data-processing?machine=%22Laser%20Welding%20Machine%202%22&KPI=%22consumption_working%22&Horizon=20
@app.get("/data-processing")
def fun(machine: str, KPI: str, Horizon: int):
    # Example calculations
    # final_path = f'{models_path}{machine}_{KPI}.json'
    f_CharacterizeKPI.characterize_KPI(machine,KPI)
    # if not os.path.isfile(final_path):
    #     f_CharacterizeKPI.characterize_KPI(machine,KPI)
    #     print('NO')
    # else:
    #     print('YES')
    
    result_dates, result_values = f_CharacterizeKPI.make_prediction(machine, KPI, Horizon)
    out_dict = {
        'Machine_name': machine,
        'KPI_name': KPI,
        'Predicted_value': result_values,
        'Measure_unit': '',
        'Date_prediction': result_dates,
        'Forecast': True
    }
    return {"result": out_dict.tolist()}  # Convert numpy array to list for JSON serialization

if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0") # potrebbe essere bloccante

    # m = 'Medium Capacity Cutting Machine 1'
    # k = 'consumption'
    # x,y = data_load(m,k)
    # plt.plot(x,y)
    # characterize_KPI('Medium Capacity Cutting Machine 1', 'consumption')
