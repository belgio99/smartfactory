import os
import pydruid.db
import requests
from constants import DRUID_URL

def get_db_connection():
    return pydruid.db.connect(
                host=os.getenv('DRUID_HOST'),
                port=int(os.getenv('DRUID_PORT')),
                path='/druid/v2/sql/',
                scheme='http'
            )

def query_db(query: str):
    query_obj = {
        "query": query
    }
    return requests.post(DRUID_URL, json=query_obj)
