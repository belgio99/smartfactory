import os
druid_host = os.getenv('DRUID_HOST')
druid_post = os.getenv('DRUID_PORT')

FRONTEND_HOST = "http://localhost:8080"
DRUID_URL = f"http://{druid_host}:{druid_post}/druid/v2/sql"