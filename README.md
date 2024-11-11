# SmartFactory RAG API

This project provides an API endpoint to answer questions based using Retrieval-Augmented Generation (RAG). It combines online and offline language models for question answering, with a fallback to the offline model when an internet connection is unavailable.

## Table of Contents
- [Requirements](#requirements)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Running the Application](#running-the-application)
- [Usage](#usage)

## Requirements

- Python 3.8+
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://langchain.com/)
- [Chroma](https://docs.trychroma.com/)
- [dotenv](https://pypi.org/project/python-dotenv/)
- [socket](https://docs.python.org/3/library/socket.html)

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/belgio99/smartfactory.git
   cd smartfactory
   git checkout RAG
   cd RAG
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Llama 3.2 (1B Parameters) Locally**:
	To set up the Llama 3.2 model with 1 billion parameters on your local machine, follow these steps: 
	- Download and install [Ollama](https://ollama.com/download), a platform that facilitates running language models locally. 
	- Once installed, you can execute the following command to run the Llama 3.2 (1B) model: ```bash
    ollama run llama3.2:1b
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

## Project Structure

- `main.py`: Application entry point.
- `routers`: Directory containing API routers.
- `schemas`: Directory containing Pydantic models for request and response validation.
- `docs/filtered_dataset.csv`: The dataset used for document embeddings.

## Running the Application

1. **Start the FastAPI server**:
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000`.

## Usage

Send a POST request to the `/ask` endpoint with a question as input.

### Example Request

```json
{
  "text": "What is the average working time for machine X?"
}
```

### Example Response

```json
{
  "text": "The average working time for machine X is 120 minutes."
}
```