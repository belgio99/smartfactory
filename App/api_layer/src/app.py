from fastapi.responses import JSONResponse
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from model.alert import Alert
from model.settings import DashboardSettings
from notification_service import send_notification, retrieve_notifications
from database.connection import get_db_connection, query_db_with_params, close_connection
from constants import *
import logging

from api_auth import get_verify_api_key
from model.user import *
from typing import Annotated
import json


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
        connection = get_db_connection() #TODO - Fix when we'll have a more stable version of the database
        cursor = connection.cursor()
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
        query = "SELECT * FROM Users WHERE "+("Email" if body.isEmail else "Username")+"=%s"
        response = query_db_with_params(cursor, connection, query, (body.user,))
        logging.info(response)
        if (len(response) == 0):
            raise HTTPException(status_code=404, detail="User not found")
        elif (response[0][4] != body.password): #TODO encoding/decoding of psw
            raise HTTPException(status_code=400, detail="Wrong credentials")
        #TODO auth token
        close_connection(connection, cursor)
        return UserInfo(userId=str(response[0][0]), username=response[0][1], email=response[0][2], role=response[0][3], site=response[0][5])
    except HTTPException as e:
        logging.error("HTTPException: %s", e.detail)
        close_connection(connection, cursor)
        raise e
    except Exception as e:
        logging.error("Exception: %s", str(e))
        close_connection(connection, cursor)
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
    try:
        connection, cursor = get_db_connection()
        query = "SELECT UserID FROM Users WHERE UserID=%s"
        response = query_db_with_params(cursor, connection, query, (int(userId),))
        logging.info(response)
        if (len(response) == 0):
            raise HTTPException(status_code=404, detail="User not found")
        #TODO auth token
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
    try:
        connection, cursor = get_db_connection()
        query = "SELECT UserID FROM Users WHERE Email=%s"
        response = query_db_with_params(cursor, connection, query, (body.email,))
        logging.info(response)
        if (len(response) != 0):
            raise HTTPException(status_code=404, detail="User already registered")
        query_insert = "INSERT INTO Users (Username, Email, Role, Password, SiteName) VALUES (%s, %s, %s, %s, %s) RETURNING UserID;"
        cursor.execute(query_insert, (body.username, body.email, body.role, body.password, body.site,)) #TODO encode psw
        #TODO auth token
        userid = cursor.fetchone()[0]
        close_connection(connection, cursor)
        return UserInfo(userId=str(userid), username=body.username, email=body.email, role=body.role, site=body.site)
    except HTTPException as e:
        logging.error("HTTPException: %s", e.detail)
        close_connection(connection, cursor)
        raise e
    except Exception as e:
        logging.error("Exception: %s", str(e))
        close_connection(connection, cursor)
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
    #TODO REMOVE, ONLY FOR TESTING
    conn, cur = get_db_connection()
    if cur:
        print("Cursor obtained successfully")
        # Don't forget to close the connection and cursor when done
        create_table_queries = [
            """
            CREATE TABLE IF NOT EXISTS Users (
            UserID SERIAL PRIMARY KEY,
            Username VARCHAR(50) NOT NULL,
            Email VARCHAR(50) NOT NULL,
            Role VARCHAR(20) NOT NULL,
            Password VARCHAR(50) NOT NULL,
            SiteName VARCHAR(50) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Reports (
            ReportID SERIAL PRIMARY KEY,
            Name VARCHAR(100) NOT NULL,
            Type VARCHAR(100) NOT NULL,
            OwnerID INT NOT NULL,
            GeneratedAt TIMESTAMP NOT NULL,
            FilePath TEXT NOT NULL,
            SiteName VARCHAR(50) NOT NULL,
            FOREIGN KEY (OwnerID) REFERENCES Users(UserID)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Alerts (
            AlertID VARCHAR(36) PRIMARY KEY,
            Title VARCHAR(255) NOT NULL,
            Type VARCHAR(255) NOT NULL,
            Description VARCHAR(255) NOT NULL,
            TriggeredAt TIMESTAMP NOT NULL,
            MachineName VARCHAR(255) NOT NULL,
            isPush BIT NOT NULL,
            Recipients VARCHAR(255) NOT NULL,
            Severity VARCHAR(10) NOT NULL
            CHECK (Severity IN ('Low', 'Medium', 'High'))
            )
            """
        ]

        for query in create_table_queries:
            response = cur.execute(query)
            conn.commit()
            print(response)

        insert_users_query = """
        INSERT INTO Users (Username, Email, Role, Password, SiteName) VALUES
        ('john_doe', 'john@example.com', 'admin', 'password123', 'SiteA'),
        ('jane_smith', 'jane@example.com', 'user', 'password456', 'SiteB'),
        ('alice_jones', 'alice@example.com', 'user', 'password789', 'SiteC')
        """
        cur.execute(insert_users_query)
        conn.commit()
        #print("Dummy data inserted into Users table")
        #get_users_query = """
        #SELECT username, email FROM Users
        #"""
        #cur.execute(get_users_query)
        #conn.commit()
        #print("Data retrieved from Users table")
        #rows = cur.fetchall()
        #for row in rows:
        #    print(row)
        cur.close()
        conn.close()
        
    uvicorn.run(app, port=8000, host="0.0.0.0")