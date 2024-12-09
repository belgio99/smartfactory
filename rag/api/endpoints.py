import httpx
import json
import os

from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv

from fastapi import APIRouter, Depends
from schemas.promptmanager import PromptManager
from chains.ontology_rag import DashboardGenerationChain, GeneralQAChain, KPIGenerationChain
from schemas.models import Question, Answer
from schemas.XAI_rag import RagExplainer

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.graphs import RdfGraph
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache
from collections import deque
from dotenv import load_dotenv
#from .api_auth.api_auth import get_verify_api_key

from datetime import datetime
from dateutil.relativedelta import relativedelta

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# History length parameter
HISTORY_LEN = 3

# Load environment variables
load_dotenv()

def create_graph(source_file):
    """
    Creates an RDF graph from the specified file.
    
    Args:
        source_file (str): The file path for the RDF source.
    
    Returns:
        RdfGraph: An RDFGraph instance created from the source file.
    """
    graph = RdfGraph(
        source_file=source_file,
        serialization="xml",
        standard="rdf"
    )
    return graph

class FileUpdateHandler(FileSystemEventHandler):
    """
    Handler for monitoring file modifications. Reloads the RDF graph when the file changes.
    """
    def on_modified(self, event):
        """
        Called when a file modification is detected.
        
        Args:
            event (FileSystemEvent): The event triggered by the file modification.
        """
        if event.src_path.endswith(os.environ['KB_FILE_NAME']):
            print(f"Detected change in {os.environ['KB_FILE_NAME']}. Reloading the graph...")
            global graph
            del graph
            graph = create_graph(os.environ['KB_FILE_PATH'] + os.environ['KB_FILE_NAME'])
            graph.load_schema()
            global history
            history = deque(maxlen=HISTORY_LEN)

# Initialize the RDF graph
graph = create_graph(os.environ['KB_FILE_PATH'] + os.environ['KB_FILE_NAME'])
graph.load_schema()

# Set up the file system observer
event_handler = FileUpdateHandler()
observer = Observer()
observer.schedule(event_handler, os.environ['KB_FILE_PATH'], recursive=True)
observer.start()

# Initialize the LLM model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
#set_llm_cache(InMemoryCache())

# Initialize the conversation history deque
history = deque(maxlen=HISTORY_LEN)

# FastAPI router initialization
router = APIRouter()

# Initialize the prompt manager
prompt_manager = PromptManager('prompts/')

def format_docs(docs):
    """
    Helper function to format documents for the prompt.
    
    Args:
        docs (list): A list of documents to be formatted.
    
    Returns:
        str: A formatted string of the document contents.
    """
    return "\n\n".join(doc.page_content for doc in docs)

def toDate(data):
    """
    Converts a date range string into a valid date format.
    
    Args:
        data (str): The date range or single date string to be converted.
    
    Returns:
        str: The formatted date range string.
    """
    TODAY = datetime.now()
    FIRST_DAY = "2024-03-01"

    if "->" in data:
        date = data
    elif data == "NULL":
        date = f"{FIRST_DAY}->{(TODAY - relativedelta(days=1)).strftime('%Y-%m-%d')}"
    else:
        temp = data.split("=")
        _type = temp[0]
        _value = int(temp[1])
        delta = 0
        if _type == "days":
            delta = relativedelta(days=_value)
        elif _type == "weeks":
            delta = relativedelta(weeks=_value)
        elif _type == "months":
            delta = relativedelta(months=_value)
        elif _type == "years":
            delta = relativedelta(years=_value)
        
        if delta == relativedelta():
            date = f"{(TODAY - delta).strftime('%Y-%m-%d')}->{(TODAY - delta).strftime('%Y-%m-%d')}"
        else:
            date = f"{(TODAY - delta).strftime('%Y-%m-%d')}->{(TODAY - relativedelta(days=1)).strftime('%Y-%m-%d')}"
    return date

def prompt_classifier(input: Question):
    """
    Classifies an input prompt into a predefined category and generates the associated URL if needed.
    
    Args:
        input (Question): The user input question to be classified.
    
    Returns:
        tuple: A tuple containing the label and the corresponding URL (if applicable).
    """
    # Format the conversation history
    history_context = "CONVERSATION HISTORY:\n" + "\n\n".join(
        [f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history]
    )

    esempi = [
        {"text": "Predict for the next month the cost_working_avg for Large Capacity Cutting Machine 2 based on last three months data", "label": "predictions"},
        {"text": "Generate a new kpi named machine_total_consumption which use some consumption kpis to be calculated", "label": "new_kpi"},
        {"text": "Compute the Maintenance Cost for the Riveting Machine 1 for yesterday", "label": "kpi_calc"},
        {"text": "Can describe cost_working_avg?", "label": "kb_q"},
        {"text": "Make a report about bad_cycles_min for Laser Welding Machine 1 with respect to last week", "label": "report"},
        {"text": "Create a dashboard to compare performances for different type of machines", "label": "dashboard"},
    ]

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

    # If the label requires a URL generation
    url = ""
    if label == "predictions" or label == "kpi_calc":
        # Format the conversation history again
        history_context = "CONVERSATION HISTORY:\n" + "\n\n".join(
            [f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history]
        )

        esempi = [
            {"testo": "Predict for tomorrow the Energy Cost Working Time for Large Capacity Cutting Machine 2 based on last week data", "data": f"Energy Cost Working Time, Large Capacity Cutting Machine 2, weeks=1, days=1"},
            {"testo": "Predict the future Power Consumption Efficiency for Riveting Machine 2 over the next 5 days", "data": f"Power Consumption Efficiency, Riveting Machine 2, NULL, days=5"},
            {"testo": "Can you calculate Machine Utilization Rate for Assembly Machine 1 for yesterday?", "data": f"Machine Utilization Rate,  Assembly Machine 1, days=1, NULL"},
            {"testo": "Calculate Machine Usage Trend for Laser Welding Machine 1 for today", "data": f"Machine Usage Trend, Laser Welding Machine 1, days=0, NULL"},
            {"testo": "Calculate for the last 2 weeks Cost Per Unit for Laser Welding Machine 2", "data": f"Cost Per Unit, Laser Welding Machine 2, weeks=2, NULL"},
            {"testo": "Can you predict for the future 3 weeks the Energy Cost Working Time for Large Capacity Cutting Machine 2 based on 24/10/2024 data?", "data": f"Energy Cost Working Time, Large Capacity Cutting Machine 2, 2024-10-24->2024-10-24, weeks=3"}
        ]

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
        data = data.content.strip("\n").split(": ")[1].split(", ")

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
    """
    Function to query the KPI engine for machine data.

    This function mocks a response from an external KPI engine API using httpx
    and returns the data about machine power consumption.

    Args:
        url (str): The URL endpoint for the KPI engine API.

    Returns:
        dict: A dictionary containing the success status and the KPI data.
            If the request is successful, the data will be in the 'data' field.
            Otherwise, the error message will be in the 'error' field.
    """
    kpi_engine_url = "https://kpi.engine.com/api"  

    mock_response = httpx.Response(
      status_code=200,
      json=[{
        'Machine name': 'Laser Cutter',
        'KPI name': 'power',
        'Value': '0,055',
        'Unit of Measure': 'kW',
        'Date': '12/10/2024',
        'Forecast': False
        },
        {
        'Machine name': 'Riveting Machine',
        'KPI name': 'power',
        'Value': '0,07',
        'Unit of Measure': 'kW',
        'Date': '12/10/2024',
        'Forecast': False
        },
        ])

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
    """
    Function to query the predictor engine for machine prediction data.

    This function mocks a response from an external predictor engine API 
    and returns predicted values related to machine operation.

    Args:
        url (str): The URL endpoint for the predictor engine API.

    Returns:
        dict: A dictionary containing the success status and the prediction data.
            If the request is successful, the data will be in the 'data' field.
            Otherwise, the error message will be in the 'error' field.
    """
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
    """
    Handles the response from the predictor engine.

    This function processes the predictor engine response and formats it
    into a string representation of the prediction data.

    Args:
        url (str): The URL endpoint for the predictor engine API.

    Returns:
        str: A string representing the prediction data formatted for the response.
    """
    response = await ask_predictor_engine(url)
    response = ",".join(json.dumps(obj) for obj in response['data'])
    return response

async def handle_new_kpi(question: Question, llm, graph, history):
    """
    Handles the generation of new KPIs based on user input.

    This function invokes a KPI generation chain to create a new KPI based on
    the user's question and returns the result.

    Args:
        question (Question): The question object containing user input.
        llm: The language model used for invoking the chain.
        graph: The knowledge graph used for processing the input.
        history: The conversation history for context.

    Returns:
        str: The generated KPI response based on the user's input.
    """
    kpi_generation = KPIGenerationChain(llm, graph, history)
    response = kpi_generation.chain.invoke(question.userInput)
    return response['result']

async def handle_report(url):
    """
    Handles the generation of a report by querying both the predictor and KPI engines.

    This function fetches data from both engines and formats it into a report string.

    Args:
        url (str): The URL endpoint for the engine APIs.

    Returns:
        str: A formatted report string containing both KPI and prediction data.
    """
    predictor_response = await ask_predictor_engine(url)
    kpi_response = await ask_kpi_engine(url)
    predictor_response = ",".join(json.dumps(obj) for obj in predictor_response['data'])
    kpi_response = ",".join(json.dumps(obj) for obj in kpi_response['data'])
    return "PRED_CONTEXT:" + predictor_response + "\nENG_CONTEXT:" + kpi_response

async def handle_dashboard(question: Question, llm, graph, history):
    """
    Handles the generation of a dashboard based on the user's input.

    This function processes the user's query for dashboard elements and generates
    a contextual response to bind the dashboard's KPI and GUI elements.

    Args:
        question (Question): The question object containing user input.
        llm: The language model used for invoking the chain.
        graph: The knowledge graph used for processing the input.
        history: The conversation history for context.

    Returns:
        str: The response string containing both knowledge base and GUI elements context.
    """
    with open("docs/gui_elements.json", "r") as f:
        chart_types = json.load(f)
    gui_elements = json.dumps(chart_types["charts"]).replace('‘', "'").replace('’', "'")
    gui_elements = ",".join(json.dumps(element) for element in chart_types["charts"])
    dashboard_generation = DashboardGenerationChain(llm, graph, history)
    response = dashboard_generation.chain.invoke(question.userInput)
    return 'KB_CONTEXT:' + response['result'] + '\n GUI_CONTEXT:' + gui_elements

async def handle_kpi_calc(url):
    """
    Handles KPI calculations by querying the KPI engine.

    This function sends a request to the KPI engine using the provided URL, processes 
    the response data, and returns it as a formatted string.

    Args:
        url (str): The URL endpoint for the KPI engine API.

    Returns:
        str: A string containing the KPI calculation data in a formatted form.
    """
    response = await ask_kpi_engine(url)
    response = ",".join(json.dumps(obj) for obj in response['data'])
    return response

async def handle_kb_q(question: Question, llm, graph, history):
    """
    Handles a Knowledge Base query by invoking the GeneralQAChain.

    This function processes the user's question and uses the GeneralQAChain to 
    generate a response based on the knowledge graph and the conversation history.

    Args:
        question (Question): The question object containing the user's input.
        llm (object): The language model used to generate responses.
        graph (object): The knowledge graph used to provide context for the response.
        history (list): A list of previous conversation entries to provide context.

    Returns:
        str: The response generated by the GeneralQAChain.
    """
    general_qa = GeneralQAChain(llm, graph, history)
    response = general_qa.chain.invoke(question.userInput)
    return response['result']

async def translate_answer(question: Question, question_language: str, context):
    """
    Translates the generated response into the user's preferred language.

    This function formats a prompt to translate the response content into the specified 
    language and invokes the language model to perform the translation.

    Args:
        question (Question): The question object containing the user's input.
        question_language (str): The language to translate the response into.
        context (str): The context or generated response that needs to be translated.

    Returns:
        str: The translated response.
    """
    prompt = prompt_manager.get_prompt('translate').format(
        _HISTORY_='',
        _CONTEXT_=context,
        _USER_QUERY_=question.userInput,
        _LANGUAGE_=question_language
    )
    print(f"Translating response to {question_language}")
    return llm.invoke(prompt)


@router.post("/chat", response_model=Answer)
#async def ask_question(question: Question, api_key: str = Depends(get_verify_api_key(["api-layer"]))): # to add or modify the services allowed to access the API, add or remove them from the list in the get_verify_api_key function e.g. get_verify_api_key(["gui", "service1", "service2"])
async def ask_question(question: Question): # to add or modify the services allowed to access the API, add or remove them from the list in the get_verify_api_key function e.g. get_verify_api_key(["gui", "service1", "service2"])    
    language_prompt = prompt_manager.get_prompt('get_language').format(
        _HISTORY_='',
        _CONTEXT_='',
        _USER_QUERY_=question.userInput
    )
    translated_question = llm.invoke(language_prompt).content
    question_language, question.userInput = translated_question.split("-", 1)

    print(f"Question Language: {question_language} - Translated Question: {question.userInput}")

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
        
        if question_language.lower() != "english":
            llm_result = await translate_answer(question, question_language, llm_result.content)
            
        # Update the history
        history.append({'question': question.userInput.replace('{','{{').replace('}','}}'), 'answer': llm_result.content.replace('{','{{').replace('}','}}')})
        return Answer(textResponse=llm_result.content, textExplanation='', data='query', label='kb_q') # da rivedere

    # Execute the handler
    context = await handlers[label]()

    if label == 'kb_q':
        if question_language.lower() != "english":
            context = await translate_answer(question, question_language, context)
            context = context.content

        # Update the history
        history.append({'question': question.userInput.replace('{','{{').replace('}','}}'), 'answer': context.replace('{','{{').replace('}','}}')})
        return Answer(textResponse=context, textExplanation='', data='', label=label)

    # Generate the prompt and invoke the LLM for certain labels
    if label in ['predictions', 'new_kpi', 'report', 'kpi_calc', 'dashboard']:
        # Prepare the history context from previous chat
        history_context = "CONVERSATION HISTORY:\n" + "\n\n".join(
            [f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history]
        )
        # Prepare the prompt and invoke the LLM
        prompt = prompt_manager.get_prompt(label).format(
            _HISTORY_=history_context,
            _USER_QUERY_=question.userInput,
            _CONTEXT_=context
        )
        llm_result = llm.invoke(prompt)
        
        if question_language.lower() != "english":
            llm_result = await translate_answer(question, question_language, llm_result.content)

        history.append({'question': question.userInput.replace('{','{{').replace('}','}}'), 'answer': llm_result.content.replace('{','{{').replace('}','}}')})

        explainer = RagExplainer(threshold = 15.0,)

        if label == 'predictions':
            # Response: Chat response, Explanation: TODO, Data: No data to send            
            explainer.add_to_context([("Predictor", "["+context+"]")])
            textResponse, textExplanation, _ = explainer.attribute_response_to_context(llm_result.content)
            return Answer(textResponse=textResponse, textExplanation=textExplanation, data='', label=label)

        if label == 'kpi_calc':
            # Response: Chat response, Explanation: TODO, Data: No data to send            
            explainer.add_to_context([("KPI Engine", "["+context+"]")])
            textResponse, textExplanation, _ = explainer.attribute_response_to_context(llm_result.content)
            return Answer(textResponse=textResponse, textExplanation=textExplanation, data="", label=label)

        if label == 'new_kpi':
            # Response: KPI json as list, Explanation: TODO, Data: KPI json to be sended to T1
            context_cleaned = context.replace("```", "").replace("json\n", "").replace("json", "").replace("```", "")
            explainer.add_to_context([("Knowledge Base", context_cleaned)])
            textResponse, textExplanation, _ = explainer.attribute_response_to_context(llm_result.content)
            return Answer(textResponse=textResponse, textExplanation=textExplanation, data=llm_result.content, label=label) 

        if label == 'report':
            # Response: No chat response, Explanation: TODO, Data: Report in str format
            pred_context, eng_context = context.removeprefix("PRED_CONTEXT:").split("ENG_CONTEXT:")
            pred_context = "["+pred_context+"]"
            eng_context = "["+eng_context+"]"
            explainer.add_to_context([("Predictor", pred_context), ("KPI Engine", eng_context)])
            
            textResponse, textExplanation, _ = explainer.attribute_response_to_context(llm_result.content)
            return Answer(textResponse="", textExplanation=textExplanation, data=textResponse, label=label)

        if label == 'dashboard':
            # Response: Chat response, Explanation: TODO, Data: Binding KPI-Graph elements
            # TODO: separare il chat response dal binding nel prompt
            kb_context, gui_context = context.removeprefix("KB_CONTEXT:").split("GUI_CONTEXT:")
            kb_context = kb_context.replace("```", "").replace("json\n", "").replace("json", "").replace("```", "")
            gui_context = "["+gui_context+"]"
            explainer.add_to_context([("Knowledge Base", kb_context), ("GUI Elements", gui_context)])
            
            # Converting the JSON string to a dictionary
            response_cleaned = llm_result.content.replace("```", "").replace("json\n", "").replace("json", "").replace("```", "")
            response_json = json.loads(response_cleaned)
            
            textResponse, textExplanation, _ = explainer.attribute_response_to_context(response_json["textualResponse"])
            data = json.dumps(response_json["bindings"], indent=2)
            return Answer(textResponse=textResponse, textExplanation=textExplanation, data=data, label=label)