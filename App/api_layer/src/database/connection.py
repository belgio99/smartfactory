import os
import pydruid.db

def get_db_connection():
    return pydruid.db.connect(
                host=os.getenv('DRUID_HOST'),
                port=int(os.getenv('DRUID_PORT')),
                path='/druid/v2/sql/',
                scheme='http'
            )