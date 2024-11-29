import f_CharacterizeKPI
import f_forecasting
import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/data-processing")
def fun():
    return {'hello': 5}

if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0") # potrebbe essere bloccante

    m = 'Medium Capacity Cutting Machine 1'
    k = 'consumption'
    x,y = data_load(m,k)
    plt.plot(x,y)
    characterize_KPI('Medium Capacity Cutting Machine 1', 'consumption')
