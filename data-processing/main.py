import f_dataprocessing
import uvicorn

from storage.storage_operations import retrieve_all_models_from_storage
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
import os
import datetime
import asyncio

from api_auth.api_auth import get_verify_api_key

from model import Json_out, Json_in, Json_out_el, LimeExplainationItem, Severity


async def task_scheduler():
    """Central scheduler running periodic tasks"""
    while True:
        await asyncio.sleep(2)
        new_data_polling()
        print('polling_complete :)')
        await asyncio.sleep(86400)
        # await asyncio.sleep(10)
            

async def lifespan(app: FastAPI):
    """Lifespan context manager to start and stop the scheduler"""
    scheduler_task = asyncio.create_task(task_scheduler())
    try:
        yield
    finally:
        scheduler_task.cancel()
        await scheduler_task

app = FastAPI(lifespan = lifespan)

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
    return retrieve_all_models_from_storage()
    # return 'Hello public World :)'

@app.get("/data-processing/_private")
def hello_world(api_key: str = Depends(get_verify_api_key(["ai-agent","api-layer"]))):
    return 'Hello private World :)'

# ACTUAL PREDICTIONS
@app.post("/data-processing/predict", response_model = Json_out)
def predict(JSONS: Json_in, api_key: str = Depends(get_verify_api_key(["ai-agent","api-layer"]))): # to add or modify the services allowed to access the API, add or remove them from the list in the get_verify_api_key function e.g. get_verify_api_key(["gui", "service1", "service2"])
    """
        given a series of couple MACHINE-KPI and an integer value N, this function predicts
        the next N data points given a certain trained model. If the model does not exist yet
        it is created, trained, and stored in json format for future use.
        This function also returns explainability results to help the user understand how certain
        we are about the given prediction.

        Args:
        JSONS: the list of tuples to be used for prediction
        api_key: authentication to allow only selected container to access this function

        Returns:
        a list of dictionaries containing:
        Machine_name: str -> the name of the machine used
        KPI_name: str -> the KPI id
        Predicted_value: Optional[List[float]] -> list of predictions
        Lower_bound: List[float] -> list of upper certainty bounds
        Upper_bound: List[float] -> list of lower certainty bounds
        Confidence_score: List[float] -> chance to actually find the value inside the bounds
        Lime_explaination: List[float] -> explaination of which components contribute more to the prediction
        Measure_unit: str -> unit of the KPI
        Date_prediction: List[str] -> list of dates regarding the predicted values
        Forecast: bool
    """
    out_dicts = []
    for json_in in JSONS.value:
        machine = json_in.Machine_name#['Machine_name'] #direttamente valore DB
        KPI_name = json_in.KPI_name#['KPI_name']
        json_out_el = Json_out_el(
            Machine_name= machine,
            KPI_name= KPI_name,
            Predicted_value=[],
            Lower_bound=[],
            Upper_bound=[],
            Confidence_score=[],
            Lime_explaination=[],
            Measure_unit="",
            Date_prediction=[],
            Error_message="",
            Forecast=True
        )

        KPI_data = f_dataprocessing.kpi_exists(machine,KPI_name, API_key)
 
        if KPI_data['Status'] == 0:
            if KPI_data['forecastable'] == True:
                horizon = json_in.Date_prediction#['Date_prediction']
                # today = datetime.datetime.now().date()
                # delta = req_date - today
                # horizon = delta.days() 
                if horizon > 0:
                    
                    if not f_dataprocessing.check_model_exists(machine,KPI_name):
                       f_dataprocessing.characterize_KPI(machine,KPI_name)
                    result = f_dataprocessing.make_prediction(machine, KPI_name, horizon)

                    json_out_el.Predicted_value = result['Predicted_value']
                    json_out_el.Lower_bound = result['Lower_bound']
                    json_out_el.Upper_bound = result['Upper_bound']
                    json_out_el.Measure_unit = KPI_data["unit_measure"]
                    json_out_el.Confidence_score = result['Confidence_score']

                    Lime_exp = []
                    for exp in result['Lime_explaination']:
                        Lime_exp.append([LimeExplainationItem(date_info=item[0], value=item[1]) for item in exp])
                    json_out_el.Lime_explaination = Lime_exp
                    json_out_el.Date_prediction = result['Date_prediction']                  
                else:
                    json_out_el.Error_message = 'Errore, la data inserita è precedente alla data odierna'
            else:
                json_out_el.Error_message = 'Errore, il KPI inserito non esiste'
            out_dicts.append(json_out_el)

    json_out = Json_out(
    value=out_dicts
    )
    return json_out.dict()

def new_data_polling():
    """
        daily check of new data point to update the models. new data points are extracted 24 hours
        if an error occurs it is reported to the user and if drift is detected the re-training of
        the code is performed

        Args:

        Returns:
    """
    # query_body = {
    #     "query": f"SELECT * FROM JSONS" #TODO make sure that it retrieves all jsons
    # }
    # response = f_dataprocessing.execute_druid_query(query_body)
    # #TODO: link response to available models
    # availableModels = []
    availableModels = []
    for m in availableModels:
        f_dataprocessing.elaborate_new_datapoint(m['Machine_name'], m['KPI_name'])
    print(datetime.datetime.today())
    alert_data = {
     'title': "A",
     'type': "V",
     'description': "Desc",
     'machine': "Machine",
     'isPush': True,
     'isEmail': True,
     'recipients': ["FactoryFloorManager"],
     'severity': Severity.MEDIUM
    }
    url_alert = f"http://api:8000/smartfactory/postAlert"
    f_dataprocessing.send_Alert(url_alert,alert_data,API_key)
 
if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0") # potrebbe essere bloccante
    
    # m = 'Medium Capacity Cutting Machine 1'
    # k = 'consumption'
    # x,y = data_load(m,k)
    # plt.plot(x,y)
    # characterize_KPI('Medium Capacity Cutting Machine 1', 'consumption')





