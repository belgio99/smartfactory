import f_dataprocessing
import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
import os
import datetime
from api_auth.api_auth import get_verify_api_key

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

# @app.get("/data-processing/load_model")
# def test():
#     return f_dataprocessing.load_model('Large Capacity Cutting Machine 1','consumption')

# @app.get("/data-processing/test_model_save")
# def test():
#     return f_dataprocessing.characterize_KPI('Large Capacity Cutting Machine 1','consumption')

# TEST CONNECTIONS
@app.get("/data-processing/_public")
def hello_world():
    return 'Hello public World :)'

@app.get("/data-processing/_private")
def hello_world(api_key: str = Depends(get_verify_api_key(["ai-agent"]))):
    return 'Hello private World :)'

# ACTUAL PREDICTIONS
#http://localhost:8000/data-processing?machine=%22Laser%20Welding%20Machine%202%22&KPI=%22consumption_working%22&Horizon=20
# @app.post("/data-processing/predict", response_model = Json_out)
@app.post("/data-processing/predict")
def predict(JSONS: Json_in, api_key: str = Depends(get_verify_api_key(["ai-agent"]))): # to add or modify the services allowed to access the API, add or remove them from the list in the get_verify_api_key function e.g. get_verify_api_key(["gui", "service1", "service2"])
    out_dicts = []
    for json_in in JSONS:
        # json_in = {}
        # json_in = {
        #     "Machine_name": 'Large Capacity Cutting Machine 1',
        #     "KPI_name": 'consumption',
        #     "Date_prediction": 5
        # }
        machine = json_in['Machine_name'] #direttamente valore DB
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
        host_url = 'kb'
        host_port = '8000'
        KPI_data = f_dataprocessing.kpi_exists(machine,KPI_name,host_url,host_port)
        # KPI_data = {
        #     "Status": 0,
        #     "forecastable": True,
        #     "unit_measure": "BAU"
        # }

        if KPI_data['Status'] == 0:
            if KPI_data['forecastable'] == True:
                horizon = json_in['Date_prediction']
                # today = datetime.datetime.now().date()
                # delta = req_date - today
                # horizon = delta.days() 
                if horizon > 0:
                    if not f_dataprocessing.check_model_exists(machine,KPI_name):
                       f_dataprocessing.characterize_KPI(machine,KPI_name)
                    result = f_dataprocessing.make_prediction(machine, KPI_name, horizon)
                   
                    out_dict['Predicted_value'] = result['Predicted_value']
                    out_dict['Lower_bound'] = result['Lower_bound']
                    out_dict['Upper_bound'] = result['Upper_bound']
                    out_dict['Measure_unit'] = KPI_data["unit_measure"]
                    out_dict['Confidence_score'] = result['Confidence_score']
                    out_dict['Lime_explaination'] = result['Lime_explaination']
                    out_dict['Date_prediction'] = result['Date_prediction']                  
                else:
                    out_dict['Predicted_value'] = 'Errore, la data inserita è precedente alla data odierna'
            else:
                out_dict['Predicted_value'] = 'Errore, il KPI inserito non esiste'
            out_dicts.append(out_dict)
    return {"result": out_dicts}  # Convert numpy array to list for JSON serialization


#TEST FOR OUTPUT FORMAT
@app.get("/data-processing/Test_predict")
def predict(JSONS: Json_in, api_key: str = Depends(get_verify_api_key(["ai-agent"]))): # to add or modify the services allowed to access the API, add or remove them from the list in the get_verify_api_key function e.g. get_verify_api_key(["gui", "service1", "service2"])
    out_dicts = []
    for json_in in JSONS:
        json_in = {}
        json_in = {
            "Machine_name": 'Large Capacity Cutting Machine 1',
            "KPI_name": 'consumption',
            "Date_prediction": 5
        }
        machine = json_in['Machine_name'] #direttamente valore DB
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
        host_url = 'kb'
        host_port = '8000'
        # KPI_data = f_dataprocessing.kpi_exists(machine,KPI_name,host_url,host_port)
        KPI_data = {
            "Status": 0,
            "forecastable": True,
            "unit_measure": "BAU"
        }

        if KPI_data['Status'] == 0:
            if KPI_data['forecastable'] == True:
                horizon = json_in['Date_prediction']
                # today = datetime.datetime.now().date()
                # delta = req_date - today
                # horizon = delta.days() 
                if horizon > 0:
                    if not f_dataprocessing.check_model_exists(machine,KPI_name):
                       f_dataprocessing.characterize_KPI(machine,KPI_name)
                    result = f_dataprocessing.make_prediction(machine, KPI_name, horizon)
                    print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAaa')
                    print(result)
                   
                    out_dict['Predicted_value'] = result['Predicted_value']
                    out_dict['Lower_bound'] = result['Lower_bound']
                    out_dict['Upper_bound'] = result['Upper_bound']
                    out_dict['Measure_unit'] = KPI_data["unit_measure"]
                    out_dict['Confidence_score'] = result['Confidence_score']
                    out_dict['Lime_explaination'] = result['Lime_explaination']
                    out_dict['Date_prediction'] = result['Date_prediction']                  
                else:
                    out_dict['Predicted_value'] = 'Errore, la data inserita è precedente alla data odierna'
            else:
                out_dict['Predicted_value'] = 'Errore, il KPI inserito non esiste'
            out_dicts.append(out_dict)
    return {"result": out_dicts}  # Convert numpy array to list for JSON serialization




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





