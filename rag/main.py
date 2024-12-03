from fastapi import FastAPI
from api import endpoints

app = FastAPI()

app.include_router(endpoints.router)