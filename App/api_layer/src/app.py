from fastapi.responses import JSONResponse
import uvicorn
from fastapi import FastAPI, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from model.alert import Alert
from model.dashboard_settings import DashboardSettings
from notification_service import send_notification
from database.connection import get_db_connection
import logging
from model.user import *
from typing import Annotated


app = FastAPI()
logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.post("/postAlert")
def post_alert(alert: Alert):
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
        logging.info("Received alert with title: %s", alert.notificationTitle)
        
        if not alert.notificationTitle:
            logging.error("Missing notification title")
            raise HTTPException(status_code=400, detail="Missing notification title")
        
        if not alert.notificationText:
            logging.error("Missing notification text")
            raise HTTPException(status_code=400, detail="Missing notification text")
        
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

@app.post("/smartfactory/login")
def login(body: Login):
    """
    Endpoint to login a user.
    This endpoint receives the user credentials and logins the user if it is present in the database.
    Args:
        body (LoginModel): the login body object containing the login details.
    Returns:
        Response: A response object with status code 200 if the notification is sent successfully.
    Raises:
        HTTPException: If any validation check fails or an unexpected error occurs.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT Id, Username, Type, Email, Password FROM Users WHERE "+("Email" if body.isEmail else "Username")+"=%s"
        cursor.execute(query, (body.user))
        results = cursor.fetchall()
        if (not_found):
            raise HTTPException(status_code=404, detail="User not found")
        elif (wrong_psw):
            raise HTTPException(status_code=404, detail="Wrong credentials")
        resp = UserInfo()
        return resp
    except HTTPException as e:
        logging.error("HTTPException: %s", e.detail)
        raise e
    except Exception as e:
        logging.error("Exception: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/smartfactory/logout")
def logout(user: str):
    #TODO logout DB
    return Response(status_code=status.HTTP_200_OK)

@app.post("/smartfactory/register", status_code=status.HTTP_201_CREATED)
def register(body: Register):
    #TODO register DB
    if (found):
        raise HTTPException(status_code=400, detail="User already registered")
    return {"test":"testvalue"}

@app.get("/smartfactory/dashboardSettings/{dashboardId}")
def load_dashboard_settings(dashboardId: str):
    '''
    Endpoint to load dashboard settings from the Database.
    This endpoint receives a dashboard ID and returns the corresponding settings fetched from the DB.
    Args:
        dashboardId (str): The ID of the dashboard.
    Returns:
        dashboard_settings: DashboardSettings object containing the settings.
    Raises:
        HTTPException: If the settings are not found or an unexpected error occurs.

    '''
    pass # Placeholder for the implementation

@app.post("/smartfactory/dashboardSettings/{dashboardId}")
def save_dashboard_settings(dashboardId: str, dashboard_settings: DashboardSettings):
    '''
    Endpoint to save dashboard settings to the Database.
    This endpoint receives a dashboard ID and the settings to be saved and saves them to the DB.
    Args:
        dashboardId (str): The ID of the dashboard.
        dashboard_settings (DashboardSettings): The settings to be saved.
    Returns:
        Response: A response object with status code 200 if the settings are saved successfully.
    Raises:
        HTTPException: If the settings are invalid or an unexpected error occurs.
        
    '''
    pass # Placeholder for the implementation


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")