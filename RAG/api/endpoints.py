import httpx

from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv

from fastapi import APIRouter
from schemas.promptmanager import PromptManager
from chains.ontology_rag import DashboardGenerationChain, GeneralQAChain, KPIGenerationChain
from schemas.models import Question, Answer

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.graphs import RdfGraph

# Load environment variables
load_dotenv()

graph = RdfGraph(
    source_file="docs/sa_ontology.rdf",
    serialization="xml",
    standard="rdf"
)

graph.load_schema()

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# Initialize FastAPI router
router = APIRouter()

prompt_manager = PromptManager('prompts/')

# Helper function to format documents for the prompt
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def dummy_classifier(input):
    labels = ['predictions', 'new_kpi', 'report', 'kb_q', 'dashboard','kpi_calc']
    return [labels[5], '']

async def ask_kpi_engine(url):
    kpi_engine_url = "https://kpi.engine.com/api"  

    mock_response = httpx.Response(
      status_code=200,
      json = [{
        'Machine name': 'Laser Cutter',
        'KPI name': 'power',
        'Value': '0,055',
        'Unit of Measure': 'kW',
        'Date': '12/10/2024',
        'Forecast': False
      }])

    #   json = [{
    #     "Machine_name": "Riveting Machine",
    #     "KPI_name": "idle_time",
    #     "Date": "20/10/2024",
    #     "Mean": 2.333
    #   },
    #   {
    #     "Machine_name": "Riveting Machine",
    #     "KPI_name": "idle_time",
    #     "Date": "20/10/2024",
    #     "Max": 5.0
    #   },
    #   {
    #     "Machine_name": "Riveting Machine",
    #     "KPI_name": "idle_time",
    #     "Date": "20/10/2024",
    #     "Min": 0.0
    #   },
    #   {
    #     "Machine_name": "Riveting Machine",
    #     "KPI_name": "working_time",
    #     "Date": "18/10/2024",
    #     "Mean": 180.0
    #   },
    #   {
    #     "Machine_name": "Riveting Machine",
    #     "KPI_name": "working_time",
    #     "Date": "18/10/2024",
    #     "Max": 200.0
    #   },
    #   {
    #     "Machine_name": "Riveting Machine",
    #     "KPI_name": "working_time",
    #     "Date": "18/10/2024",
    #     "Min": 133.0
    #   },
    #   {
    #     "Machine_name": "Welding Machine",
    #     "KPI_name": "idle_time",
    #     "Date": "17/10/2024",
    #     "Mean": 3.5
    #   },
    #   {
    #     "Machine_name": "Welding Machine",
    #     "KPI_name": "idle_time",
    #     "Date": "17/10/2024",
    #     "Max": 6.0
    #   },
    #   {
    #     "Machine_name": "Welding Machine",
    #     "KPI_name": "idle_time",
    #     "Date": "17/10/2024",
    #     "Min": 1.0
    #   },
    #   {
    #     "Machine_name": "Welding Machine",
    #     "KPI_name": "working_time",
    #     "Date": "22/10/2024",
    #     "Mean": 150
    #   },
    #   {
    #     "Machine_name": "Welding Machine",
    #     "KPI_name": "working_time",
    #     "Date": "22/10/2024",
    #     "Max": 190
    #   },
    #   {
    #     "Machine_name": "Welding Machine",
    #     "KPI_name": "working_time",
    #     "Date": "22/10/2024",
    #     "Min": 120
    #   }
    # ])
    
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

    # async with httpx.AsyncClient() as client: TO-DO
    #     response = await client.get(url)
    
    if response.status_code == 200:
        return {"success": True, "data": response.json()}  
    else:
        return {"success": False, "error": response.text}  
    
async def ask_predictor_engine(url):
    predictor_engine_url = "https://predictor.engine.com/api"  

    mock_response = httpx.Response(
      status_code=200,
      # json = [{
      #   'Machine name': 'Riveting Machine',
      #   'KPI name': 'idle_time',
      #   'Value': '1,12',
      #   'Forecast': True
      # },
      # {
      #   'Machine name': 'Laser Cutter',
      #   'KPI name': 'idle_time',
      #   'Value': '0,123',
      #   'Date': '12/10/2024',
      #   'Forecast': True
      # }]
      json = [{
        "Machine_name": "Riveting Machine",
        "Predicted": True,
        "KPI_name": "working_time",
        "Date": "26/11/2024",
        "avg": 112
      },
      {
        "Machine_name": "Welding Machine",
        "Predicted": True,
        "KPI_name": "working_time",
        "Date": "26/11/2024",
        "avg": 65
      }
    ])
    
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

    # async with httpx.AsyncClient() as client: TO-DO
    #     response = await client.get(url)
    
    if response.status_code == 200:
        return {"success": True, "data": response.json()}  
    else:
        return {"success": False, "error": response.text}  

async def handle_predictions(url):
    response = await ask_predictor_engine(url)
    return response['data']

async def handle_new_kpi(question, llm, graph):
    kpi_generation = KPIGenerationChain(llm, graph)
    response = kpi_generation.chain.invoke(question.text)
    return response['result']

async def handle_report(url):
    predictor_response = await ask_predictor_engine(url)
    kpi_response = await ask_kpi_engine(url)
    return predictor_response['data'] + kpi_response['data']

async def handle_dashboard(question, llm, graph):
    with open("docs/gui_elements.txt", "r") as f:
        gui_elements = f.read()
    dashboard_generation = DashboardGenerationChain(llm, graph)
    response = dashboard_generation.chain.invoke(question.text)
    return response['result'] + '\n' + gui_elements

async def handle_kpi_calc(url):
    response = await ask_kpi_engine(url)
    return response['data']

async def handle_kb_q(question, llm, graph):
    general_qa = GeneralQAChain(llm, graph)
    response = general_qa.chain.invoke(question.text)
    return response['result']

@router.post("/ask", response_model=Answer)
async def ask_question(question: Question):
    # Classify the question
    label, url = dummy_classifier(question)

    # Mapping of handlers
    handlers = {
        'predictions': lambda: handle_predictions(url),
        'new_kpi': lambda: handle_new_kpi(question, llm, graph),
        'report': lambda: handle_report(url),
        'dashboard': lambda: handle_dashboard(question, llm, graph),
        'kpi_calc': lambda: handle_kpi_calc(url),
        'kb_q': lambda: handle_kb_q(question, llm, graph),
    }

    # Check if the label is valid
    if label not in handlers:
        raise ValueError(f"Unknown label: {label}")

    # Execute the handler
    context = await handlers[label]()

    # Generate the prompt and invoke the LLM for certain labels
    if label in ['predictions', 'new_kpi', 'report', 'kpi_calc', 'dashboard']:
        prompt = prompt_manager.get_prompt(label)
        formatted_prompt = prompt.format(_CONTEXT_=context, _USER_QUERY_=question.text)
        llm_result = llm.invoke(formatted_prompt)
        return Answer(text=llm_result.content)

    # For 'kb_q', return the context directly
    return Answer(text=context)