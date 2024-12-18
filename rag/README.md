# SmartFactory RAG API

This project provides an API endpoint to answer questions based using Retrieval-Augmented Generation (RAG). It combines online and offline language models for question answering, with a fallback to the offline model when an internet connection is unavailable.

## Table of Contents
- [Requirements](#requirements)
- [Local Setup](#local-setup)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Docker Setup](#docker-setup)

## Requirements

- Python 3.8+
- pip
- Docker (if using Docker setup)

## Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/belgio99/smartfactory.git
   cd smartfactory/rag
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file**:
   Define necessary environment variables in a `.env` file in the root directory. 

## Environment Variables

Define the following in your `.env` file:

- `GOOGLE_API_KEY`: API key for [Google Generative AI](https://aistudio.google.com/apikey) if using online model.
- `LANGCHAIN_API_KEY`: API key for [LangChain](https://smith.langchain.com/) services.
- `LANGCHAIN_TRACING_V2`: Enables or disables LangChain’s tracing feature, which logs detailed traces of requests and responses. Setting this to `false` disables tracing to improve performance and privacy.
-  `LANGCHAIN_ENDPOINT`: Specifies the URL endpoint for LangChain’s API. This is the base URL that LangChain’s services use to communicate with the application. Example: `https://api.smith.langchain.com`.
- `LANGCHAIN_PROJECT`: Defines the project name for LangChain services, useful for organizing and tracking API requests and logs within LangChain’s dashboard or project management tools.
- `POSTGRES_USER`: PostgreSQL username used to connect to the API authentication database.
- `POSTGRES_DB`: Name of the PostgreSQL database used for API authentication.
- `POSTGRES_PASSWORD`: Password for the PostgreSQL user to connect to the API authentication database.
- `POSTGRES_HOST`: Host address (IP or domain) of the PostgreSQL server for API authentication.
- `POSTGRES_PORT`: Port on which the PostgreSQL server listens for connections to the API authentication database.
- `KB_FILE_PATH`: (Default: ../docs/kb/) Path to the directory containing the knowledge base files.
- `KB_FILE_NAME`: (Default: sa_ontology.rdf) Name of the knowledge base file to be used.

## Running the Application

1. **Start the FastAPI server**:
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000`.

## Usage

Send a POST request to the `/agent/chat` endpoint with a question as input.

### Example Request

```json
{
  "userInput": "How many machines are in the factory?",
  "userId": "corvus"
}
```

### Example Response

```json
{
  "text": "There are 16 machines.",
  "textExplanation": "...",
  "data": "...",
  "label": "kb_q"
}
```

## Docker Setup

### 1. Build the Docker Image  

Run the following command to build the Docker image:  

```bash
docker build -t rag.
```

### 2. Run the Docker Container

Start the container and map port 8000 (container) to 8000 (host):

```bash
docker run -p 8000:8000 --name rag-container rag
```