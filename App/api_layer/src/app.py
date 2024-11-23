from multiprocessing import connection
from fastapi.responses import JSONResponse
from pydantic import Json
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from model.alert import Alert
from model.settings import DashboardSettings
from notification_service import send_notification, retrieve_notifications
from database.connection import get_db_connection, query_db
from constants import *
import logging

from api_auth import ACCESS_TOKEN_EXPIRW_MINUTES, get_verify_api_key, SECRET_KEY, ALGORITHM, password_context, get_current_user
from model.user import *
from typing import Annotated
import json
from datetime import datetime, timedelta, timezone
from jose import jwt


app = FastAPI()
logging.basicConfig(level=logging.INFO)

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
def get_alerts(userId: str):
    list = retrieve_notifications(userId)
    return JSONResponse(content={"alerts": list}, status_code=200)

@app.post("/smartfactory/settings/{userId}")
def save_user_settings(userId: str, settings: dict):
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
        connection, cursor = get_db_connection() #TODO - Fix when we'll have a more stable version of the database
        query = "UPDATE UserSettings SET settings = %s WHERE userId = %s"
        cursor.execute(query, (json.dumps(settings), userId))
        connection.commit()
        return JSONResponse(content={"message": "Settings saved successfully"}, status_code=200)
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
        UserInfo object with the details of the user logged in.
    Raises:
        HTTPException: If any validation check fails or an unexpected error occurs.
    """
    try:
        connection, cursor = get_db_connection()
        query = "SELECT * FROM Users WHERE Username = %s"
        cursor.execute(query, (body.user,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if not result or not password_context.verify(body.password, result[4]):
            logging.error("Invalid credentials")
            raise HTTPException(status_code=401, detail="Invalid username or password")
   
        logging.info("User logged in successfully")
    
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRW_MINUTES)
        access_token = jwt.encode(
            {"sub": result[1], "role": result[3], "exp": datetime.now(timezone.utc) + access_token_expires},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        user = UserInfo(userId=result[0], username=result[1], email=result[2], type=result[3], access_token=access_token)
        return JSONResponse(content=access_token, status_code=200)
        
    except Exception as e:
        logging.error("Exception: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/smartfactory/logout")
def logout(userId: str):
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
    # Clients should delete the token from the client side
    #TODO logout DB
    if (not_found):
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(content={"message": "User logged out successfully"}, status_code=200)

@app.post("/smartfactory/register", status_code=status.HTTP_201_CREATED)
def register(body: Register):
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
    #TODO register DB
    try:
        connection, cursor = get_db_connection()
        # Check if user already exists
        query = "SELECT * FROM Users WHERE Username = %s OR Email = %s"
        cursor.execute(query, (body.username, body.email))
        user_exists = cursor.fetchone()

        if user_exists:
            logging.error("User already registered")
            raise HTTPException(status_code=400, detail="User already registered")
        else:
            hashed_password = password_context.hash(body.password)

            # Insert new user into the database
            insert_query = "INSERT INTO Users (Username, Email, Role, Password, Sitename) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (body.username, body.email, body.role, hashed_password, body.sitename))
            connection.commit()
            cursor.close()
            connection.close()
            return {"message": "User registered successfully"}

    except HTTPException as e:
        logging.error("HTTPException: %s", e.detail)
        raise e
    except Exception as e:
        logging.error("Exception: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

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