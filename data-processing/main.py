import f_dataprocessing
import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os
import datetime

from model import Json_out, Json_in

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

@app.get("/data-processing/test")
def test():
    print(f_dataprocessing.data_load('',''))





#http://localhost:8000/data-processing?machine=%22Laser%20Welding%20Machine%202%22&KPI=%22consumption_working%22&Horizon=20
@app.get("/data-processing/predict", response_model = Json_out)
def predict(JSONS: Json_in):
    d = str(datetime.datetime.today().date())
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
        machine = json_in['Machine_name']
        KPI_name = json_in['KPI_name']
        out_dict = {
            'Machine_name': machine,
            'KPI_name': KPI_name,
            'Predicted_value': '',
            'Lower_bound':[], #from XAI
            'Upper_bound':[], #from XAI
            'Confidence_score':[], #from XAI
            'Lime_explaination': [], #from XAI
            'Measure_unit': '',
            'Date_prediction': '',
            'Forecast': True
        }
        KPI_data = f_dataprocessing.kpi_exists(machine_id,kpi_id,host_url,host_port)
        if KPI_data['Status'] == 0:
            if KPI_data['forecastable'] == True:
                req_date = json_in['Date_prediction'] #TODO check date format
                today = datetime.datetime.now().date()
                delta = req_date - today
                horizon = delta.days() 
                if horizon > 0:
                    query_body = {
                        "query": f"SELECT * FROM JSONS WHERE MACHINE = MACHINE AND KPI = KPI" #TODO TODO
                    }
                    response = f_dataprocessing.execute_druid_query(query_body)
                    if not 1:#json_exists(): TODO, update with cmpleted query
                        f_dataprocessing.characterize_KPI(machine,KPI_name)
                    result_values, result_dates, lb, ub, cs, le = f_dataprocessing.make_prediction(machine, KPI_name, horizon)
                    
                    out_dict['Predicted_value'] = result_values
                    out_dict['Measure_unit'] = KPI_data["unit_measure"]
                    out_dict['Date_prediction'] = result_dates
                else:
                    out_dict['Predicted_value'] = 'Errore, la data inserita è precedente alla data odierna'
            else:
                out_dict['Predicted_value'] = 'Errore, il KPI inserito non esiste'
            out_dicts.append(out_dict)
    return {"result": out_dict.tolist()}  # Convert numpy array to list for JSON serialization

# TODO: This function should be called once a day and retreive all the models 
def new_data_polling():
    query_body = {
        "query": f"SELECT * FROM JSONS" #TODO make sure that it retrieves all jsons
    }
    response = f_dataprocessing.execute_druid_query(query_body)
    #TODO: link response to available models
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





