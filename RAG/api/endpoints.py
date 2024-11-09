import os
import asyncio
import socket
from dotenv import load_dotenv

from fastapi import APIRouter
from schemas.models import Question, Answer

from langchain_chroma import Chroma
from langchain_community.document_loaders import CSVLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

# Helper function to check internet connection
def internet(host="8.8.8.8", port=53, timeout=3):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except socket.error:
        return False
    
# Helper function to format documents for the prompt
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
    
# Load environment variables
load_dotenv()

# Load the embedding for the vector store
embeddings = HuggingFaceBgeEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)
#embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", task_type="retrieval_document")
#embeddings_offline = OllamaEmbeddings(model="llama3.2:1b")

# Initialize online language model
#llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# Initialize offline language model
llm_offline = ChatOllama(model="llama3.2:1b")

# Load documents and prepare vector store at application startup
csv_args = {"delimiter": ","}
loader = CSVLoader(file_path="docs/dataset.csv", csv_args=csv_args)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

# Create the vector store from documents
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)

# Set up retriever with custom search parameters
retriever = vectorstore.as_retriever(search_kwargs={'k': 15})

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are provided with data from a machine performance dataset. The dataset has the following columns:
    - 'time': date in ISO format
    - 'asset_id': asset identifier
    - 'name': machine name
    - 'kpi': KPI type (e.g., 'working_time', 'idle_time', 'offline_time')
    - 'sum', 'avg', 'min', 'max': aggregated values for each KPI.

    Based on the dataset and the user's question, analyze the relevant information and generate a response.

    Context:
    {context}

    User Question:
    {question}

    Please provide a clear and concise answer to the user's question, using relevant data from the context where applicable."""
)

# Initialize FastAPI router
router = APIRouter()

@router.post("/ask", response_model=Answer)
async def ask_question(question: Question):
    # Set up the RAG chain using the preloaded retriever, prompt template, and LLM
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt_template
        | ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        | StrOutputParser()
    )

    rag_chain_offline = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt_template
        | llm_offline
        | StrOutputParser()
    )
    
    # Set a timeout value (in seconds)
    timeout_seconds = 15

    if internet():
      # Invoke the chain with a timeout
      try:
          answer = await asyncio.wait_for(asyncio.to_thread(rag_chain.invoke, question.text), timeout=timeout_seconds)
      except (asyncio.TimeoutError, Exception):  # If timeout or other exception occurs
          # Use the offline model as a fallback
          print("Timeout occurred. Using offline model as a fallback.")
          answer = rag_chain_offline.invoke(question.text)
    else:
      # Use the offline model
      print("No internet connection. Using offline model.")
      answer = rag_chain_offline.invoke(question.text)
    
    return Answer(text=answer)
