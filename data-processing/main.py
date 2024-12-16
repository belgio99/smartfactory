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
from dotenv import load_dotenv
from pathlib import Path


async def task_scheduler():
    """Central scheduler running periodic tasks"""
    i = 0
    alertList = {
        'Title': ['Outlier detected', 'Outlier detected', 'missing value', 'Zero streak','Zero streak'],
        'Machine': ["Large Capacity Cutting Machine 1",
                    "Laser Welding Machine 1",
                    "Assembly Machine 2",
                    "Testing Machine 3",
                    "Testing Machine 3"],
        'Date': ["2024-04-09","2024-05-03","2024-10-19","2024-03-03","2024-03-20"],
        'Description': ['Power for Large Capacity Cutting Machine 1 reaturned a value higher than expected',
                        "consumption for Laser Welding Machine 1 returned a value higher than expected",
                        "Assembly Machine 2 did not yield a new value for: average_cycle_time",
                        "working_time for Testing Machine 3 returned zeros for 3 days in a row",
                        "working_time for Testing Machine 3 returned zeros for 20 days in a row"],
        'Type': ['unexpected output','unexpected output',
                 "Machine_unreachable","Machine_unreachable","Machine_unreachable"],
        'Recipients':[["FactoryFloorManager","SpecialityManufacturingOwner"],
                      ["FactoryFloorManager","SpecialityManufacturingOwner"],
                      ["FactoryFloorManager"],["FactoryFloorManager"]],
        'severity': [Severity.MEDIUM,Severity.MEDIUM,Severity.MEDIUM,Severity.MEDIUM,Severity.HIGH]
    }
    while True:
        await asyncio.sleep(15)
        alert_data = {
        'title': alertList["Title"][i],
        'type': alertList["Type"][i],
        'description': alertList["Description"][i],
        'machine': alertList["Machine"][i],
        'isPush': True,
        'isEmail': True,
        'alert_date': alertList["Date"][i],
        'recipients': alertList["Recipients"][i],
        'severity': alertList["severity"][i]
        }
        send_dummy_alert(alert_data)
        i+=1
        await asyncio.sleep(15)
        # new_data_polling()
        
        # #send here a bunch of alerts
        # await asyncio.sleep(86400)
        
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

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

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
        Machine_Name: str -> the name of the machine used
        KPI_Name: str -> the KPI id
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
    if len(JSONS.value) != 0:
        print(f"received a list of {len(JSONS.value)} KPIs to predict")
        for json_in in JSONS.value:
            machine = json_in.Machine_Name#['Machine_Name'] #direttamente valore DB
            KPI_Name = json_in.KPI_Name#['KPI_Name']
            json_out_el = Json_out_el(
                Machine_Name= machine,
                KPI_Name= KPI_Name,
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
            API_key = os.getenv('my_key')
            KPI_data = f_dataprocessing.kpi_exists(machine,KPI_Name, API_key)
            if KPI_data['Status'] == 0:
                print('the KPI exists')
                if KPI_data['forecastable'] == True:
                    print('the KPI is forecastable')
                    horizon = json_in.Date_prediction#['Date_prediction']
                    # today = datetime.datetime.now().date()
                    # delta = req_date - today
                    # horizon = delta.days() 
                    if horizon > 0:
                        
                        status = 0
                        if not f_dataprocessing.check_model_exists(machine,KPI_Name):
                            print(f"Creating model for {machine},{KPI_Name}")
                            status = f_dataprocessing.characterize_KPI(machine,KPI_Name)
                        if status == 0:
                            result = f_dataprocessing.make_prediction(machine, KPI_Name, horizon)
                            print(f"the output data is: {result['Predicted_value']}")

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
                            if status == -1:
                                json_out_el.Error_message = 'Error: the time-series is constant, forecast is meaningless'
                            else:
                                json_out_el.Error_message = 'Error: could not preprocess the data'

                    else:
                        json_out_el.Error_message = 'Error: invalid selected date for forecast'
                else:
                   json_out_el.Error_message = f'Error:, the KPI {KPI_Name} of {machine} is not forecastable' 
            else:
                json_out_el.Error_message = f'Error:, the KPI {KPI_Name} does not exist for {machine}'
            out_dicts.append(json_out_el)
        json_out = Json_out(
        value=out_dicts
        )
        return json_out.dict()
    else:
        json_out_el = Json_out_el(
        Machine_Name = "",
        KPI_Name= "",
        Predicted_value=[],
        Lower_bound=[],
        Upper_bound=[],
        Confidence_score=[],
        Lime_explaination=[],
        Measure_unit="",
        Date_prediction=[],
        Error_message="Received input is not valid",
        Forecast=True)

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
        f_dataprocessing.elaborate_new_datapoint(m['Machine_Name'], m['KPI_Name'])
    print(datetime.datetime.today())

def send_dummy_alert(alert_data):
    url_alert = f"http://api:8000/smartfactory/postAlert"
    API_key = os.getenv('my_key')
    f_dataprocessing.send_Alert(url_alert,alert_data,API_key)


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0") # potrebbe essere bloccante
    
    # m = 'Medium Capacity Cutting Machine 1'
    # k = 'consumption'
    # x,y = data_load(m,k)
    # plt.plot(x,y)
    # characterize_KPI('Medium Capacity Cutting Machine 1', 'consumption')





