# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY ./requirements.txt .
RUN python -m pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
      && python -m pip install --no-cache-dir -r requirements.txt

WORKDIR /data-processing
COPY . /data-processing

# Creates a non-root user with an explicit UID and adds permission to access the /tuaDirectoryBase folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /data-processing
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "App.api_layer\app:app"]
CMD [ "python", "./main.py" ]

LABEL org.opencontainers.image.source https://github.com/belgio99/smartfactory