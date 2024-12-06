import f_dataprocessing
import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os
import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


API_key = '12d326d6-8895-49b9-8e1b-a760462ac13f'

host_url = 'TBD'
host_port = 'TBD'

#http://localhost:8000/data-processing?machine=%22Laser%20Welding%20Machine%202%22&KPI=%22consumption_working%22&Horizon=20
@app.get("/data-processing/predict")
def predict(JSONS):
    d = datetime.datetime.today().date()
    out_dict = {
        'Machine_name': 'MACHINENAME :(',
        'KPI_name': 'KPINAME :)',
        'Predicted_value': [0,1,2,3,4,5,6,7,8,9,10],
        'Lower_bound':[1,1,1,1,1,1,1,1,1,1], #from XAI
        'Upper_bound':[0,0,0,0,0,0,0,0,0,0], #from XAI
        'Confidence_score':[9,8,7,6,5,4,3,2,1,0], #from XAI
        'Lime_explaination': list(('string',2.1),("2",2),("s",1)), #from XAI
        'Measure_unit': 'Kbps',
        'Date_prediction': [d,d,d,d,d,d,d,d,d,d],
        'Forecast': True
    }
    return {"result": [out_dict]}
    out_dicts = []
    
    for json_in in JSONS: 
        machine = json_in['Machine name']
        KPI_name = json_in['KPI name']
        out_dict = {
            'Machine_name': machine,
            'KPI_name': KPI_name,
            'Predicted_value': '',
            'Measure_unit': '',
            'Date_prediction': '',
            'Forecast': True
        }
        # stabilire connessione diretta con 
        is_working = 0
        if is_working:

            url_kb_KPI = f"http://{host_url}:{host_port}/kb/{KPI_name}/get_kpi?kpi_id={KPI_name}" 
            url_kb_machine = f"/kb/{machine}/get_kpi" 

            

            if 1:#kpi_exists(machine, KPI): & is it usable?
                req_date = json_in['Date_prediction']
                today = datetime.datetime.now().date()
                delta = req_date - today
                horizon = delta.days() 
                if horizon > 0:
                    if not 1:#json_exists():
                        f_dataprocessing.characterize_KPI(machine,KPI_name)
                    result_dates, result_values = f_dataprocessing.make_prediction(machine, KPI_name, horizon)
                    out_dict['Predicted_value'] = result_values
                    out_dict['Measure_unit'] = 1#recover_unit(machine,KPI)
                    out_dict['Date_prediction'] = result_dates
                else:
                    out_dict['Predicted_value'] = 'Errore, la data inserita è precedente alla data odierna'
                    return 'ERROR, invalid date'
            else:
                out_dict['Predicted_value'] = 'Errore, il KPI inserito non esiste'
                return 'ERROR, KPI ... does not exist'
            out_dicts.append(out_dict)
    else:
        d = datetime.datetime.today().date()
        out_dict = {
            'Machine_name': machine,
            'KPI_name': KPI_name,
            'Predicted_value': [0,1,2,3,4,5,6,7,8,9,10],
            'Measure_unit': 'Kbps',
            'Date_prediction': [d,d,d,d,d,d,d,d,d,d],
            'Forecast': True
        }
    return {"result": out_dict.tolist()}  # Convert numpy array to list for JSON serialization

# TODO: This function should be called once a day and retreive all the models 
def new_data_polling():
   availableModels = []
   for m in availableModels:
        f_dataprocessing.elaborate_new_datapoint(m['Machine_name'], m['KPI_name'])
 
if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0") # potrebbe essere bloccante
    
    # m = 'Medium Capacity Cutting Machine 1'
    # k = 'consumption'
    # x,y = data_load(m,k)
    # plt.plot(x,y)
    # characterize_KPI('Medium Capacity Cutting Machine 1', 'consumption')





