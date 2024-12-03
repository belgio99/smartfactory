# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY ./requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /KB
COPY . /KB

RUN apt-get update
RUN apt-get install -y apt-utils build-essential gcc

# Set environment variables for Java 11
ENV JAVA_FOLDER=jdk-11.0.2
ENV JVM_ROOT=/usr/lib/jvm

# Use OpenJDK 11 tar.gz package
ENV JAVA_PKG_NAME=openjdk-11.0.2_linux-x64_bin.tar.gz
ENV JAVA_TAR_GZ_URL=https://download.java.net/java/GA/jdk11/9/GPL/$JAVA_PKG_NAME

# Install wget, download and set up Java 11
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*    && \
    apt-get clean                                                               && \
    apt-get autoremove                                                          && \
    echo Downloading $JAVA_TAR_GZ_URL                                           && \
    wget -q $JAVA_TAR_GZ_URL                                                    && \
    tar -xvf $JAVA_PKG_NAME                                                     && \
    rm $JAVA_PKG_NAME                                                           && \
    mkdir -p /usr/lib/jvm                                                       && \
    mv ./$JAVA_FOLDER $JVM_ROOT                                                 && \
    update-alternatives --install /usr/bin/java java $JVM_ROOT/$JAVA_FOLDER/bin/java 1        && \
    update-alternatives --install /usr/bin/javac javac $JVM_ROOT/$JAVA_FOLDER/bin/javac 1     && \
    java -version

# Creates a non-root user with an explicit UID and adds permission to access the /KB folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /KB
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "App.api_layer\app:app"]
CMD [ "python", "./src/kb.py" ]

LABEL org.opencontainers.image.source https://github.com/belgio99/smartfactory