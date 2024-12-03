import json
import logging
import re
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException
import os
from passlib.context import CryptContext
from jose import JWTError, jwt
from database.connection import get_db_connection

SECRET_KEY = 'fJ0KSAxFqFiAFPxpAw7QdlUINm8yo7EB'   # DUMMY KEY, PLEASE USE os.getenv("SECRET_KEY") IN PRODUCTION
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # change this value accordingly to your requirements

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/smartfactory/login")

api_key_header = APIKeyHeader(name="X-API-Key")

def retrieve_keys(microservice_id: str):
    # Retrieve the API key for the specified microservice from the database
    connection, cursor = get_db_connection()
    if connection is None or cursor is None:
        logging.error("Database connection failed")
        return None
    try:
        query = "SELECT KEY FROM Microservices WHERE ServiceID = %s"
        cursor.execute(query, (microservice_id,))
        row = cursor.fetchone()
        if row:
            result = row[0]
        else:
            result = None
    except Exception as e:
        logging.error("Database query failed: %s", str(e))
        result = None
    finally:
        cursor.close()
        connection.close()
    return result
    
def get_verify_api_key(microservice_ids: list):
    async def verify_api_key(api_key: str = Depends(api_key_header)):
        matched_keys = [retrieve_keys(microservice_id) for microservice_id in microservice_ids]
        if api_key not in matched_keys:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return verify_api_key



async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieve the current user based on the provided JWT token.

    Args:
        token (str): The JWT token provided by the user, extracted using the OAuth2 scheme.

    Returns:
        dict: A dictionary containing user information if the token is valid.

    Raises:
        HTTPException: If the token is invalid or the user does not exist, an HTTP 401 error is raised.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logging.error("Invalid token")
            raise HTTPException(status_code=401, detail="Invalid token")
        connection, cursor = get_db_connection()
        query = "SELECT * FROM Users WHERE Username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        if not result:
            raise HTTPException(status_code=401, detail="Invalid token")
        return result
    except JWTError as e:
        logging.error("JWTError: %s", str(e))
        raise HTTPException(status_code=401, detail="Invalid token")