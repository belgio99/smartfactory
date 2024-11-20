import json
import re
from fastapi.security import APIKeyHeader
from fastapi import Depends, status, HTTPException
import os

api_key_header = APIKeyHeader(name="X-API-Key")

def retrieve_keys(microservice_id: str):
    # Retrieve the API key for the specified microservice from the database
    # For demonstration purposes, return a hardcoded value from a JSON file
    return json.load(open("./src/dummy_keys.json"))["microservice"][microservice_id]
    
def get_verify_api_key(microservice_ids: list):
    async def verify_api_key(api_key: str = Depends(api_key_header)):
        matched_keys = [retrieve_keys(microservice_id) for microservice_id in microservice_ids]
        if api_key not in matched_keys:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return verify_api_key