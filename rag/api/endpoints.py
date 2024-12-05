import httpx

from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv

from fastapi import APIRouter
from schemas.promptmanager import PromptManager
from chains.ontology_rag import DashboardGenerationChain, GeneralQAChain, KPIGenerationChain
from schemas.models import Question, Answer

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.graphs import RdfGraph
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache
from collections import deque
from dotenv import load_dotenv

from datetime import datetime
from dateutil.relativedelta import relativedelta

# History lenght parameter
HISTORY_LEN = 10

# Load environment variables
load_dotenv()

graph = RdfGraph(
    source_file="docs/sa_ontology.rdf",
    serialization="xml",
    standard="rdf"
)

graph.load_schema()

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
set_llm_cache(InMemoryCache())

history = deque(maxlen=HISTORY_LEN)

# Initialize FastAPI router
router = APIRouter()

prompt_manager = PromptManager('prompts/')
# Helper function to format documents for the prompt
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# TODO: maybe it should be moved in another file?
def toDate(data):
    TODAY = datetime.now()
    # first data available is from 2024-03-01
    FIRST_DAY = "2024-03-01"

    if "->" in data:
        date=data
    # NULL -> all dataset use case
    elif data == "NULL":
        date=f"{FIRST_DAY}->{(TODAY - relativedelta(days=1)).strftime('%Y-%m-%d')}"
    else:
        temp =data.split("=")
        _type = temp[0]
        _value = int(temp[1])
        delta = 0
        if _type == "days":
            delta= relativedelta(days=_value) 
        elif _type =="weeks":
            delta= relativedelta(weeks=_value)
        elif _type =="months":
            delta= relativedelta(months=_value)
        elif _type =="years":
            delta= relativedelta(years=_value)
        #'today' use case
        if delta == relativedelta():
            date=f"{(TODAY - delta).strftime('%Y-%m-%d')}->{(TODAY - delta).strftime('%Y-%m-%d')}"
        else:
            date=f"{(TODAY - delta).strftime('%Y-%m-%d')}->{(TODAY - relativedelta(days=1)).strftime('%Y-%m-%d')}"
    return date

# function which classify input prompt in one among six labels 
# if label == "predictions" or label == "kpi_calc", it will also return the url to communicate
def prompt_classifier(input: Question):

    # Format the history
    history_context = "CONVERSATION HISTORY:\n" + "\n\n".join(
        [f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history]
    )

    # few shots examples
    esempi = [
        {"text": "Predict for the next month the cost_working_avg for Large Capacity Cutting Machine 2 based on last three months data", "label": "predictions"},
        {"text": "Generate a new kpi named machine_total_consumption which use some consumption kpis to be calculated", "label": "new_kpi"},
        {"text": "Compute the Maintenance Cost for the Riveting Machine 1 for yesterday", "label": "kpi_calc"},
        {"text": "Can describe cost_working_avg?", "label": "kb_q"},
        {"text": "Make a report about bad_cycles_min for Laser Welding Machine 1 with respect to last week", "label": "report"},
        {"text": "Create a dashboard to compare perfomances for different type of machines", "label": "dashboard"},
    ]

    # Few shot prompt creation
    esempio_template = PromptTemplate(
        input_variables=["text", "label"],
        template="Text: {text}\nLabel: {label}\n"
    )

    few_shot_prompt = FewShotPromptTemplate(
        examples=esempi,
        example_prompt=esempio_template,
        prefix= "{history}\n\nFEW-SHOT EXAMPLES:",
        suffix="Task: Classify with one of the labels ['predictions', 'new_kpi', 'report', 'kb_q', 'dashboard','kpi_calc'] the following prompt:\nText: {text_input}\nLabel:",
        input_variables=["history", "text_input"]
    )
    prompt = few_shot_prompt.format(history=history_context, text_input=input.userInput)
    label = llm.invoke(prompt).content.strip("\n")

    # Query generation
    url=""
    if label == "predictions" or label == "kpi_calc":

        # Format the history
        history_context = "CONVERSATION HISTORY:\n" + "\n\n".join(
            [f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history]
        )
        
        esempi = [
            {"testo": "Predict for tomorrow the Energy Cost Working Time for Large Capacity Cutting Machine 2 based on last week data", "data": f"Energy Cost Working Time, Large Capacity Cutting Machine 2, weeks=1, days=1" },
            {"testo": "Predict the future Power Consumption Efficiency for Riveting Machine 2 over the next 5 days","data": f"Power Consumption Efficiency, Riveting Machine 2, NULL, days=5"},
            {"testo": "Can you calculate Machine Utilization Rate for Assembly Machine 1 for yesterday?", "data": f"Machine Utilization Rate,  Assembly Machine 1, days=1, NULL"},
            {"testo": "Calculate Machine Usage Trend for Laser Welding Machine 1 for today", "data": f"Machine Usage Trend, Laser Welding Machine 1, days=0, NULL"},
            {"testo": "Calculate for the last 2 weeks Cost Per Unit for Laser Welding Machine 2", "data": f"Cost Per Unit, Laser Welding Machine 2, weeks=2, NULL"},
            {"testo": "Can you predict for the future 3 weeks the Energy Cost Working Time for Large Capacity Cutting Machine 2 based on 24/10/2024 data?", "data": f"Energy Cost Working Time, Large Capacity Cutting Machine 2, 2024-10-24->2024-10-24, weeks=3"}
            
        ]
        # Few shot prompt creation
        esempio_template = PromptTemplate(
            input_variables=["testo", "data"],
            template="Text: {testo}\nData: {data}\n"
        )

        few_shot_prompt = FewShotPromptTemplate(
            examples=esempi,
            example_prompt=esempio_template,
            prefix= "{history}\n\nFEW-SHOT EXAMPLES:",
            suffix= "Task: Fill the Data field for the following prompt \nText: {text_input}\nData:\nThe filled field needs to contain four values as the examples above",
            input_variables=["history", "text_input"]
        )

        prompt = few_shot_prompt.format(history=history_context, text_input=input.userInput)

        data = llm.invoke(prompt)
        data=data.content.strip("\n").split(": ")[1].split(", ")

        kpi_id = data[0].lower().replace(" ","_")

        machine_id = data[1].replace(" ","")

        # first couple of dates parsing
        date=toDate(data[2]).split("->")
        url=f"http://127.0.0.1:8000/{label}/{kpi_id}/calculate?machineType={machine_id}&startTime={date[0]}&endTime={date[1]}"
        if label == "predictions":
            # second couple of dates parsing
            # a data labelled as 'predictor' should not be 'NULL', this (before in the pipeline) should be checked to be true 
            dateP = toDate(data[3]).split("->")
            url+=f"&startTimeP={dateP[0]}&endTimeP={dateP[1]}"

    return [label,url]

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

async def handle_new_kpi(question: Question, llm, graph, history):
    kpi_generation = KPIGenerationChain(llm, graph, history)
    response = kpi_generation.chain.invoke(question.userInput)
    return response['result']

async def handle_report(url):
    predictor_response = await ask_predictor_engine(url)
    kpi_response = await ask_kpi_engine(url)
    return predictor_response['data'] + kpi_response['data']

async def handle_dashboard(question: Question, llm, graph, history):
    with open("docs/gui_elements.txt", "r") as f:
        gui_elements = f.read()
    dashboard_generation = DashboardGenerationChain(llm, graph, history)
    response = dashboard_generation.chain.invoke(question.userInput)
    return response['result'] + '\n' + gui_elements

async def handle_kpi_calc(url):
    response = await ask_kpi_engine(url)
    return response['data']

async def handle_kb_q(question: Question, llm, graph, history):
    general_qa = GeneralQAChain(llm, graph, history)
    response = general_qa.chain.invoke(question.userInput)
    return response['result']

@router.post("/chat", response_model=Answer)
async def ask_question(question: Question):
    # Classify the question
    label, url = prompt_classifier(question)

    # Mapping of handlers
    handlers = {
        'predictions': lambda: handle_predictions(url),
        'new_kpi': lambda: handle_new_kpi(question, llm, graph, history),
        'report': lambda: handle_report(url),
        'dashboard': lambda: handle_dashboard(question, llm, graph, history),
        'kpi_calc': lambda: handle_kpi_calc(url),
        'kb_q': lambda: handle_kb_q(question, llm, graph, history),
    }

    # Check if the label is valid
    if label not in handlers:
        # Format the history
        history_context = "CONVERSATION HISTORY:\n" + "\n\n".join(
            [f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history]
        )
        llm_result = llm.invoke(history_context + "\n\n" + question.userInput)
        # Update the history
        history.append({'question': question.userInput, 'answer': llm_result.content})
        return Answer(textResponse=llm_result.content, textExplanation='', data='query')

    # Execute the handler
    context = await handlers[label]()

    if label == 'kb_q':
        # Update the history
        history.append({'question': question.userInput, 'answer': context})
        return Answer(textResponse=context, textExplanation='', data='query')

    # Generate the prompt and invoke the LLM for certain labels
    if label in ['predictions', 'new_kpi', 'report', 'kpi_calc', 'dashboard']:
        # Format the history
        history_context = "CONVERSATION HISTORY:\n" + "\n\n".join(
            [f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history]
        )
        prompt = prompt_manager.get_prompt(label)
        formatted_prompt = prompt.format(_HISTORY_=history_context, _CONTEXT_=context, _USER_QUERY_=question.userInput)
        llm_result = llm.invoke(formatted_prompt)

        # Update the history
        history.append({'question': question.userInput, 'answer': llm_result.content})

        return Answer(textResponse=llm_result.content, textExplanation='', data='report' if label == 'report' else 'query')

