FROM python:3.9-slim

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
CMD python setup_storage.py

