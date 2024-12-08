from typing import Annotated
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from pydantic import Json
import uvicorn
import tempfile
import json
from fastapi import Body, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from model.alert import Alert
from notification_service import send_notification, retrieve_alerts, send_report
from user_settings_service import persist_user_settings, retrieve_user_settings, persist_dashboard_settings, load_dashboard_settings
from database.connection import get_db_connection, query_db_with_params, close_connection
from database.minio_connection import *
from constants import *
import logging
from model.task import *
from contextlib import asynccontextmanager
import asyncio
import requests
from api_auth.api_auth import ACCESS_TOKEN_EXPIRE_MINUTES, get_verify_api_key, SECRET_KEY, ALGORITHM, password_context
from langchain_core.prompts import PromptTemplate
from model.user import *
from model.report import ReportResponse, Report, ScheduledReport
from dotenv import load_dotenv
# TODO: how to import modules from rag directory ??
from model.agent import Answer
from datetime import datetime, timedelta, timezone
from jose import jwt
from fpdf import FPDF
import os

logging.basicConfig(level=logging.INFO)

tasks = dict()
tasks_lock = asyncio.Lock()


async def task_scheduler():
    """Central scheduler that runs periodic tasks."""
    while True:
        async with tasks_lock:
            for t in tasks.values():
                if t.shouldRun():
                    await t.run()
        await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to start and stop the scheduler."""
    scheduler_task = asyncio.create_task(task_scheduler())
    try:
        yield 
    finally:
        scheduler_task.cancel()  # Cancel the scheduler on application shutdown
        await scheduler_task  # Ensure it exits cleanly

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/smartfactory/postAlert")
async def post_alert(alert: Alert, api_key: str = Depends(get_verify_api_key(["data"]))):
    """
    Endpoint to post an alert.
    This endpoint receives an alert object and processes it by sending notifications
    based on the alert's properties. It performs several validation checks on the 
    alert object before sending the notification.
    Args:
        alert (Alert): The alert object containing notification details.
    Returns:
        Response: A response object with status code 200 if the notification is sent successfully.
    Raises:
        HTTPException: If any validation check fails or an unexpected error occurs.
    """

    try:
        logging.info("Received alert with title: %s", alert.description)
        
        if not alert.title:
            logging.error("Missing notification title")
            raise HTTPException(status_code=400, detail="Missing notification title")
        
        if not alert.description:
            logging.error("Missing notification description")
            raise HTTPException(status_code=400, detail="Missing notification description")
        
        if not alert.isPush and not alert.isEmail:
            logging.error("No notification method selected")
            raise HTTPException(status_code=400, detail="No notification method selected")
        
        if not alert.recipients or len(alert.recipients) == 0:
            logging.error("No recipients specified")
            raise HTTPException(status_code=400, detail="No recipients specified")
        
        logging.info("Sending notification")
        send_notification(alert)
        logging.info("Notification sent successfully")

        return JSONResponse(content={"message": "Notification sent successfully"}, status_code=200)
    except HTTPException as e:
        logging.error("HTTPException: %s", e.detail)
        raise e
    except ValueError as e:
        logging.error("ValueError: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except TypeError as e:
        logging.error("TypeError: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error("Exception: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logging.error("Exception: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/smartfactory/alerts/{userId}")
def get_alerts(userId: str, api_key: str = Depends(get_verify_api_key(["gui"]))):
    """
    Retrieve alerts for a given user and return them as a JSON response.

    Args:
        userId (str): The ID of the user for whom to retrieve alerts.

    Returns:
        JSONResponse: A JSON response containing the list of alerts for the user.
    """
    logging.info("Retrieving alerts for user: %s", userId)
    list = retrieve_alerts(userId)
    logging.info("Alerts retrieved successfully for user: %s", userId)

    return JSONResponse(content={"alerts": list}, status_code=200)

@app.post("/smartfactory/settings/{userId}")
def save_user_settings(userId: str, settings: dict, api_key: str = Depends(get_verify_api_key(["gui"]))):
    """
    Endpoint to save user settings.
    This endpoint receives a user ID and a JSON object with the settings to be saved.
    Args:
        userId (str): The ID of the user.
        settings (dict): The settings to be saved.
    Returns:
        Response: A response object with status code 200 if the settings are saved successfully.
    Raises:
        HTTPException: If an unexpected error occurs.
    """
    try:
        if persist_user_settings(userId, settings) == False:
            raise HTTPException(status_code=404, detail="User not found")
        
        return JSONResponse(content={"message": "Settings saved successfully"}, status_code=200)
    except Exception as e:
        logging.error("Exception: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/smartfactory/settings/{userId}")
def get_user_settings(userId: str, api_key: str = Depends(get_verify_api_key(["gui"]))):
    """
    Endpoint to get user settings.
    This endpoint receives a user ID and returns the settings for that user.
    Args:
        userId (str): The ID of the user.
    Returns:
        dict: A dictionary containing the user settings.
    Raises:
        HTTPException: If an unexpected error occurs.
    """
    try:
        settings = retrieve_user_settings(userId)
        return JSONResponse(content=settings, status_code=200)
    except Exception as e:
        logging.error("Exception: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/smartfactory/login")
def login(body: Login, api_key: str = Depends(get_verify_api_key(["gui"]))):
    """
    Endpoint to login a user.
    This endpoint receives the user credentials and logins the user if it is present in the database.
    Args:
        body (LoginModel): the login body object containing the login details.
    Returns:
        UserInfo object with the details of the user logged in.
    Raises:
        HTTPException: If any validation check fails or an unexpected error occurs.
    """
    try:
        connection, cursor = get_db_connection()
        query = "SELECT * FROM Users WHERE "+("Email" if body.isEmail else "Username")+"=%s"
        response = query_db_with_params(cursor, connection, query, (body.user,))

        if not response or (body.password != response[0][4]):
            logging.error("Invalid credentials")
            raise HTTPException(status_code=401, detail="Invalid username or password")
   
        result = response[0]
        close_connection(connection, cursor)
        logging.info("User logged in successfully")
    
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = jwt.encode(
            {"sub": result[1], "role": result[3], "exp": datetime.now(timezone.utc) + access_token_expires},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        logging.info(result)
        user = UserInfo(userId=result[0], username=result[1], email=result[2], role=result[3], access_token=access_token, site=result[5])
        return JSONResponse(content=user.to_dict(), status_code=200)
    
    except HTTPException as e:
        logging.error("HTTPException: %s", e.detail)
        close_connection(connection, cursor)
        raise e
    except Exception as e:
        logging.error("Exception: %s", str(e))
        close_connection(connection, cursor)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/smartfactory/logout")
def logout(userId: str, api_key: str = Depends(get_verify_api_key(["gui"]))):
    """
    Endpoint to logout a user.
    This endpoint receives the userId and logouts the user if it is present in the database.
    Args:
        body (userId): the id of the user to logout.
    Returns:
        JSONResponse 200
    Raises:
        HTTPException: If the user is not present in the database.
    """
    try:
        connection, cursor = get_db_connection()
        query = "SELECT UserID FROM Users WHERE UserID=%s"
        response = query_db_with_params(cursor, connection, query, (int(userId),))
        logging.info(response)
        if (len(response) == 0):
            raise HTTPException(status_code=404, detail="User not found")
        #TODO delete auth token client side or db if you decide to add it from db
        close_connection(connection, cursor)
        return JSONResponse(content={"message": "User logged out successfully"}, status_code=200)
    except HTTPException as e:
        logging.error("HTTPException: %s", e.detail)
        close_connection(connection, cursor)
        raise e
    except Exception as e:
        logging.error("Exception: %s", str(e))
        close_connection(connection, cursor)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/smartfactory/register", status_code=status.HTTP_201_CREATED)
def register(body: Register, api_key: str = Depends(get_verify_api_key(["gui"]))):
    """
    Endpoint to register a user.
    This endpoint receives the user info and inserts a new user if it is not present in the database.
    Args:
        body (Register): the user details of the new user.
    Returns:
        UserInfo object with the details of the user created.
    Raises:
        HTTPException: If the user is already present in the database.
    """
    try:
        connection, cursor = get_db_connection()
        # Check if user already exists
        query = "SELECT * FROM Users WHERE Username = %s OR Email = %s"
        response = query_db_with_params(cursor, connection, query, (body.username, body.email))
        user_exists = response
        logging.info(user_exists)

        if user_exists:
            logging.error("User already registered")
            raise HTTPException(status_code=400, detail="User already registered")
        else:

            # Insert new user into the database
            query_insert = "INSERT INTO Users (Username, Email, Role, Password, SiteName) VALUES (%s, %s, %s, %s, %s) RETURNING UserID;"
            cursor.execute(query_insert, (body.username, body.email, body.role, body.password, body.site))
            connection.commit()
            userid = cursor.fetchone()[0]
            close_connection(connection, cursor)
            return UserInfo(userId=str(userid), username=body.username, email=body.email, role=body.role, site=body.site, access_token='')

    except HTTPException as e:
        logging.error("HTTPException: %s", e.detail)
        close_connection(connection, cursor)
        raise e
    except Exception as e:
        logging.error("Exception: %s", str(e))
        close_connection(connection, cursor)
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/smartfactory/user/{userId}", status_code=status.HTTP_201_CREATED)
def change_password(userId: str, body: ChangePassword, api_key: str = Depends(get_verify_api_key(["gui"]))):
    """
    Endpoint to change a user's password.
    This endpoint receives the user id and the old password inserted, and updates the user's password if the old password is correct.
    Args:
        body (ChangePassword): the user details of the user, including both the new and old password.
    Returns:
        UserInfo object with the details of the user created.
    Raises:
        HTTPException: If the user is not present in the database, the old password is incorrect, or an unexpected error occurs
    """
    try:
        connection, cursor = get_db_connection()   
        # Check if old password is correct
        query = "SELECT Password FROM Users WHERE UserID = %s"
        response = query_db_with_params(cursor, connection, query, (userId,))
        if not response:
            raise HTTPException(status_code=401, detail="User not found")
        try:
            if not body.old_password == response[0][0]:
                logging.error("Invalid old password")
                return JSONResponse(content={"message": "Invalid old password"}, status_code=401)
        except ValueError as e:
            #logging.error("Password not hashed")
            raise HTTPException(status_code=500, detail=f"ERROR: {str(e)}")
                
        # Update user password in the database
        query_update = "UPDATE Users SET password = %s WHERE UserID = %s;"
        cursor.execute(query_update, (body.new_password, userId))
        connection.commit()
        # check if updated correctly
        result = cursor.rowcount
        if result == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        close_connection(connection, cursor)
        return JSONResponse(content={"message": "Password changed successfully"}, status_code=200)
    
    except HTTPException as e:
        logging.error("HTTPException: %s", e.detail)
        close_connection(connection, cursor)
        raise e

    except Exception as e:
        logging.error("Exception: %s", str(e))
        close_connection(connection, cursor)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/smartfactory/dashboardSettings/{userId}")
def retrieve_dashboard_settings(userId: str, api_key: str = Depends(get_verify_api_key(["gui"]))):
    '''
    Endpoint to load dashboard disposition from the Database.
    This endpoint receives a user ID and returns the JSON string containing the (tree-like) disposition of the user's dashboards.
    Args:
        userId (str): The ID of the user of whom to retrieve data.
    Returns:
        dashboard_settings: JSON string containing the dashboard disposition.
    Raises:
        HTTPException: If the settings are not found or an unexpected error occurs.

    '''
    try:
        settings = load_dashboard_settings(userId)
        return JSONResponse(content=settings, status_code=200)
    except Exception as e:
        logging.error("Exception: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
   

@app.post("/smartfactory/dashboardSettings/{userId}")
def post_dashboard_settings(userId: str, dashboard_settings: dict, api_key: str = Depends(get_verify_api_key(["gui"]))):
    '''
    Endpoint to save the dashboard disposition to the Database.
    This endpoint receives a user ID and a JSON string with the dashboard disposition to be saved.
    Args:
        userId (str): The ID of the user.
        dashboard_settings (dict): The dashboard disposition to be saved.
    Returns:
        Response: A response object with status code 200 if the dashboard disposition is saved successfully.
    Raises:
        HTTPException: If an unexpected error occurs.
        
    '''
    try:
        if persist_dashboard_settings(userId, dashboard_settings) == False:
            raise HTTPException(status_code=404, detail="User not found")
        
        return JSONResponse(content={"message": "Settings saved successfully"}, status_code=200)
    except Exception as e:
        logging.error("Exception: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/smartfactory/reports")
def retrieve_reports(userId: str, api_key: str = Depends(get_verify_api_key(["gui"]))):
    try:
        connection, cursor = get_db_connection()   
        query = "SELECT ReportID, Name, Type, FilePath FROM Reports WHERE OwnerID = %s"
        response = query_db_with_params(cursor, connection, query, (int(userId),))
        if not response or response[0] is None:
            logging.info("No reports for userID %s", str(userId))
            return JSONResponse(content={"data": []}, status_code=200)
        reports = []
        for row in response:
            reports.append(ReportResponse(id=row[0], name=row[1], type=row[2]))
        close_connection(connection, cursor)
        return JSONResponse(content={"data": reports}, status_code=200)
    except Exception as e:
        logging.error("Exception: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/smartfactory/reports/download/{report_id}")
def download_report(report_id: int, api_key: str = Depends(get_verify_api_key(["gui"]))):
    try:
        connection, cursor = get_db_connection()   
        query = "SELECT ReportID, Name, OwnerID, FilePath FROM Reports WHERE ReportID = %s"
        response = query_db_with_params(cursor, connection, query, (report_id,))
        if not response or response[0] is None:
            raise HTTPException(status_code=404, detail="Report not found")
        file_name = response[0][1]
        ownerID = response[0][2]
        tmp_path = "/tmp/"+ownerID+"_"+file_name+".pdf"
        minio = get_minio_connection()
        download_object(minio, "/reports/"+ownerID, file_name, tmp_path)
        close_connection(connection, cursor)
        return FileResponse(
            path=tmp_path,
            media_type="application/pdf",
            filename="downloaded_example.pdf"
        )
    except HTTPException as e:
        logging.error("HTTPException: %s", e.detail)
        close_connection(connection, cursor)
        raise e
    except Exception as e:
        close_connection(connection, cursor)
        logging.error("Exception: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
def call_ai_agent(input: str):
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': os.getenv('API_KEY')
    }
    body = {
        'userInput': input
    }
    print(f"sending request to RAG API: {body}")
    response = requests.post(os.getenv('RAG_API_ENDPOINT'), headers=headers, json=body)
    response.raise_for_status()
    return response

def create_pdf(text: str, path: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 100, text)
    pdf.output(name=path, dest="F")
    
@app.post("/smartfactory/reports/generate", status_code=status.HTTP_201_CREATED)
def generate_report(userId: Annotated[str, Body()], params: Annotated[Report, Body()], is_scheduled: bool = False, api_key: str = Depends(get_verify_api_key(["gui"]))):
    try:
        connection, cursor = get_db_connection()   
        query = "SELECT UserID FROM Users WHERE UserID = %s"
        response = query_db_with_params(cursor, connection, query, (int(userId),))
        if not response:
            logging.error("User not found")
            raise HTTPException(status_code=404, detail="User not found")
        userId = response[0][0]
        prompt = PromptTemplate(
            input_variables=["period", "kpi", "machines"],
            template=(
                "Generate the periodic report for the period {period}, including the "
                "following KPIs: {kpi}; the KPIs concern the specified machines: {machines}."
            )        
        )
        filled_prompt = prompt.format(
            period=params.period,
            kpi=",".join(params.kpis),
            machines=",".join(params.machines)
        )
        ai_response = call_ai_agent(filled_prompt).json()
        logging.info(ai_response)
        answer = Answer.model_validate(ai_response)
        report_data = answer.textResponse
        tmp_path = "/tmp/"+userId+"_"+params.name+".pdf"
        obj_path = "/reports/"+userId+"/"+params.name+params.period+".pdf"
        create_pdf(report_data, tmp_path)
        minio = get_minio_connection()
        upload_object(minio, "/reports/"+userId, params.name+".pdf", tmp_path)
        query_insert = "INSERT INTO Reports (Name, Type, OwnerId, GeneratedAt, FilePath, SiteName) VALUES (%s, %s, %s, %s, %s, %s) RETURNING ReportID, Name, Type;"
        cursor.execute(query_insert, (params.name+".pdf", params.type or "Standard", int(userId), datetime.now(), obj_path, "Test",))
        connection.commit()
        close_connection(connection, cursor)
        if is_scheduled:
            return (params.name, params.email, tmp_path)
        return FileResponse(
            path=tmp_path,
            media_type="application/pdf",
            filename="downloaded_example.pdf"
        )
    except HTTPException as e:
        logging.error("HTTPException: %s", e.detail)
        close_connection(connection, cursor)
        raise e
    except Exception as e:
        logging.error("Exception: %s", str(e))
        close_connection(connection, cursor)
        raise HTTPException(status_code=500, detail=str(e))
    
def generate_and_send_report(userId: str, email: str, params: ScheduledReport, api_key: str):
    logging.info("Started scheduled report generation")
    report_name, to_email, tmp_path = generate_report(userId, params, True, api_key)
    send_report(to_email, report_name, tmp_path)

@app.get("/smartfactory/reports/schedule")
def retrieve_schedules(userId: str, api_key: str = Depends(get_verify_api_key(["gui"]))):
    schedules = []
    minio = get_minio_connection()
    objects = minio.list_objects(bucket_name="/settings/"+"userId", )
    for ob in objects:
        logging.info(ob)
    #TODO get schedules from DB
    return JSONResponse(content={"data": schedules}, status_code=200)

@app.post("/smartfactory/reports/schedule", status_code=status.HTTP_200_OK)
async def schedule_report(userId: Annotated[str, Body()], params: Annotated[ScheduledReport, Body()], api_key: str = Depends(get_verify_api_key(["gui"]))):
    try:
        connection, cursor = get_db_connection()   
        query = "SELECT UserID, Email FROM Users WHERE UserID = %s"
        response = query_db_with_params(cursor, connection, query, (int(userId),))
        if not response:
            logging.error("User not found")
            raise HTTPException(status_code=404, detail="User not found")
        email = response[0][1]
        close_connection(connection, cursor)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as temp_file:
            json.dump(params.model_dump(), temp_file, indent=4)
            tmp_path = temp_file.name
            logging.info(tmp_path)
            minio = get_minio_connection()
            #TODO update object if id is populated
            upload_object(minio, "/settings/"+userId, params.name+"_scheduling.json", tmp_path)
        async with tasks_lock:
            tasks[str(params.id)] = Task(func=generate_and_send_report, args=(userId, email, params, api_key), delay=params.recurrence.seconds, start_date=params.startDate)
    except HTTPException as e:
        logging.error("HTTPException: %s", e.detail)
        close_connection(connection, cursor)
        raise e
    except Exception as e:
        logging.error("Exception: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/smartfactory/agent", response_model=Answer)
def ai_agent_interaction(userInput: Annotated[str, Body(embed=True)], api_key: str = Depends(get_verify_api_key(["gui"]))):
    """
    Endpoint to interact with the AI agent.
    This endpoint receives user input and forwards it to the AI agent, then returns the generated response.
    
    Args:
        userInput (str): The user input to be processed by the AI agent.
    Returns:
        AgentResponse: The response generated by the AI agent.
    Raises:
        HTTPException: If the input is empty or an unexpected error occurs.
    """
    if not userInput:
        logging.error("Empty input")
        raise HTTPException(status_code=500, detail="Empty user input")
    # TODO: find where to store the env variables and how to retrieve them
    try:
        # Send the user input to the RAG API and get the response
        response = call_ai_agent(userInput)
        # Send the response to the user 
        answer = response.json()
        return answer

    except Exception as e:
        logging.error("Exception: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/smartfactory/dummy")
async def dummy_endpoint(api_key: str = Depends(get_verify_api_key(["gui"]))):
    """
    Dummy endpoint for testing purposes.
    Returns:
        JSONResponse: A JSON response with a dummy message.
    """
    return JSONResponse(content={"message": "This is a dummy endpoint"}, status_code=200)


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")

   