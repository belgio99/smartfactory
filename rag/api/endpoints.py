import httpx
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv

from fastapi import APIRouter, Depends
from schemas.promptmanager import PromptManager
from chains.ontology_rag import DashboardGenerationChain, GeneralQAChain, KPIGenerationChain
from schemas.models import Question, Answer
from schemas.XAI_rag import RagExplainer
from queryGen.QueryGen import QueryGenerator

from langchain_community.graphs import RdfGraph
from langchain.prompts import PromptTemplate,FewShotPromptTemplate

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

# agent header for authenticatication with other modules communication
HEADER = {"x-api-key":"06e9b31c-e8d4-4a6a-afe5-fc7b0cc045a7"}
# History length parameter
HISTORY_LEN = 1

# Load environment variables
load_dotenv()
import nltk
nltk.download('punkt_tab')


def create_graph(source_file):
    """
    Creates an RDF graph from the specified file, retrying every 30 seconds until successful.
    
    Args:
        source_file (str): The file path for the RDF source.
    
    Returns:
        RdfGraph: An RDFGraph instance created from the source file.
    """
    while True:
        try:
            graph = RdfGraph(
                source_file=source_file,
                serialization="xml",
                standard="rdf"
            )
            return graph
        except FileNotFoundError:
            print(f"Source file {source_file} not found. Retrying in 30 seconds...")
            time.sleep(30)

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
            history = {}

# Initialize the RDF graph
graph = create_graph(os.environ['KB_FILE_PATH'] + os.environ['KB_FILE_NAME'])
graph.load_schema()

# Set up the file system observer
"""event_handler = FileUpdateHandler()
observer = Observer()
observer.schedule(event_handler, os.environ['KB_FILE_PATH'], recursive=True)
observer.start()"""

# Initialize the LLM model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
#set_llm_cache(InMemoryCache())

# Initialize the conversation history deque
history = {}

# FastAPI router initialization
router = APIRouter()

# Initialize the prompt manager
prompt_manager = PromptManager('prompts/')

# Initialize the query generator
query_gen = QueryGenerator(llm)


def prompt_classifier(input: Question):
    """
    Classifies an input prompt into a predefined category and generate if needed a json query to make requests to kpi engine and predictor.
    
    Args:
        input (Question): The user input question to be classified.
    
    Returns:
        tuple: A tuple containing the label and the extracted json_obj from the input (if applicable).
    """

    esempi = [
        {"text": "Predict for the next month the cost_working_avg for Large Capacity Cutting Machine 2 based on last three months data", "label": "predictions"},
        {"text": "Generate a new kpi named machine_total_consumption which use some consumption kpis to be calculated", "label": "new_kpi"},
        {"text": "Compute the Maintenance Cost for the Riveting Machine 1 for yesterday", "label": "kpi_calc"},
        {"text": "Can you describe cost_working_avg?", "label": "kb_q"},
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
        prefix= "FEW-SHOT EXAMPLES:",
        suffix="Task: Classify with one of the labels ['predictions', 'new_kpi', 'report', 'kb_q', 'dashboard','kpi_calc'] the following prompt:\nText: {text_input}\nLabel:",
        input_variables=["text_input"]
    )

    prompt = few_shot_prompt.format(text_input=input.userInput)
    label = llm.invoke(prompt).content.strip("\n")
    print(f"user input request label = {label}")
    # If the label requires is kps_calc, report or predictions, it requires the query generator to generate a json_request from the query
    json_request=""
    all_kpis=0
    if label == "predictions" or label == "kpi_calc" or label == "report":
        json_request, all_kpis = query_gen.query_generation(input, label)
        
    return label, json_request, all_kpis

async def ask_kpi_engine(json_body):
    """
    Function to query the KPI engine for machine data.

    This function mocks a response from an external KPI engine API using httpx
    and returns the data about machine power consumption.

    Args:
        json_body (str): the json used to communicate the request to the KPI engine API.

    Returns:
        dict: A dictionary containing the success status and the KPI data.
            If the request is successful, the data will be in the 'data' field.
            Otherwise, the error message will be in the 'error' field.
    """
    kpi_engine_url = "http://smartfactory-kpi-engine-1:8000/kpi/calculate"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(kpi_engine_url,json=json_body,headers=HEADER)
        except Exception as e:
            return {
                    "success": False,
                    "data": [
                        {"Value": "Error: KPI engine is not available"}
                    ]
                }
    if response.status_code == 200:
        return {"success": True, "data": response.json()}  
    else:
        return {
                    "success": False,
                    "data": [
                        {"Value": "Error: KPI engine is not available"}
                    ]
                }

async def ask_predictor_engine(json_body):
    """
    Function to query the predictor engine for machine prediction data.

    This function mocks a response from an external predictor engine API 
    and returns predicted values related to machine operation.

    Args:
        json_body (str): the json used to communicate the request to the predictor engine API.

    Returns:
        dict: A dictionary containing the success status and the prediction data.
            If the request is successful, the data will be in the 'data' field.
            Otherwise, the error message will be in the 'error' field.
    """
    predictor_engine_url = "http://data-processing:8000/data-processing/predict" 
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url=predictor_engine_url,json=json_body,headers=HEADER)
        except Exception as e:
            return {
                    "success": False,
                    "data": {
                        "value": [
                            {"Error_message": "Predictor engine is not available"}
                        ]
                    }
                }
    
    if response.status_code == 200:
        return {"success": True, "data": response.json()}  
    else:
        return {
                    "success": False,
                    "data": {
                        "value": [
                            {"Error_message": "Predictor engine is not available"}
                        ]
                    }
                }

async def handle_predictions(json_body):
    """
    Handles the response from the predictor engine.

    This function processes the predictor engine response and formats it
    into a string representation of the prediction data.

    Args:
        json_body (str): the json used to communicate the request to the predictor engine API.

    Returns:
        str: A string representing the prediction data formatted for the response.
    """
    response = await ask_predictor_engine(json_body)

    if response['success'] == True:
        for item in response['data']['value']:
            if 'Lime_explaination' in item:
                del item['Lime_explaination']

        response = ",".join(json.dumps(obj) for obj in response['data']['value'])
    else:
        response = json.dumps(response['data'])

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

async def handle_report(json_objs):
    """
    Handles the generation of a report by querying both the predictor and KPI engines.

    This function fetches data from both engines and formats it into a report string.

    Args:
        json_objs : array of json request to kpi engine and predictor.

    Returns:
        str: A formatted report string containing both KPI and prediction data.
    """
    predictor_response = await ask_predictor_engine(json_objs[1])

    if predictor_response['success'] == True:
        for item in predictor_response['data']['value']:
            if 'Lime_explaination' in item:
                del item['Lime_explaination']

        predictor_response = ",".join(json.dumps(obj) for obj in predictor_response['data']['value'])
    else:
        predictor_response = json.dumps(predictor_response['data'])

    kpi_response = await ask_kpi_engine(json_objs[0])

    if kpi_response['success'] == True:
        kpi_response = ",".join(json.dumps(obj) for obj in kpi_response['data'])
    else:
        kpi_response = json.dumps(kpi_response['data'])
        
    print("report context:","PRED_CONTEXT:" + predictor_response + "\nENG_CONTEXT:" + kpi_response)

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

async def handle_kpi_calc(json_body):
    """
    Handles KPI calculations by querying the KPI engine.

    This function sends a request to the KPI engine using the provided URL, processes 
    the response data, and returns it as a formatted string.

    Args:
        json_body (str): the json used to communicate the request to the KPI engine API.

    Returns:
        str: A string containing the KPI calculation data in a formatted form.
    """
    response = await ask_kpi_engine(json_body)

    if response['success'] == True:
        response = ",".join(json.dumps(obj) for obj in response['data'])
    else:
        response = json.dumps(response['data'])
    
    print(response)
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
        _CONTEXT_=context,
        _USER_QUERY_=question.userInput,
        _LANGUAGE_=question_language
    )
    print(f"Translating response to {question_language}")
    return llm.invoke(prompt)


@router.post("/chat", response_model=Answer)
#async def ask_question(question: Question, api_key: str = Depends(get_verify_api_key(["api-layer"]))): # to add or modify the services allowed to access the API, add or remove them from the list in the get_verify_api_key function e.g. get_verify_api_key(["gui", "service1", "service2"])
async def ask_question(question: Question): # to add or modify the services allowed to access the API, add or remove them from the list in the get_verify_api_key function e.g. get_verify_api_key(["gui", "service1", "service2"])    
    try:
        explainer = RagExplainer(threshold = 15.0,)
        # Extract the user ID
        userId = question.userId

        if userId not in history:
            history[userId] = deque(maxlen=HISTORY_LEN)

        # Translate the question to English
        language_prompt = prompt_manager.get_prompt('get_language').format(
            _USER_QUERY_=question.userInput
        )
        translated_question = llm.invoke(language_prompt).content
        question_language, question.userInput = translated_question.split("-", 1)

        print(f"Question Language: {question_language} - Translated Question: {question.userInput}")

        # Classify the question
        label, json_body,all_kpis = prompt_classifier(question)
        # Mapping of handlers
        handlers = {
            'predictions': lambda: handle_predictions(json_body),
            'new_kpi': lambda: handle_new_kpi(question, llm, graph, history[userId]),
            'report': lambda: handle_report(json_body),
            'dashboard': lambda: handle_dashboard(question, llm, graph, history[userId]),
            'kpi_calc': lambda: handle_kpi_calc(json_body),
            'kb_q': lambda: handle_kb_q(question, llm, graph, history[userId]),
        }

        # Check if the label is not in the handlers (i.e. extra-domain question)
        if label not in handlers:
            # Format the history
            history_context = "CONVERSATION HISTORY:\n" + "\n\n".join(
                [f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history[userId]]
            )
            llm_result = llm.invoke(history_context + "\n\n" + question.userInput)
            
            # Update the history
            history[userId].append({'question': question.userInput.replace('{','{{').replace('}','}}'), 'answer': llm_result.content.replace('{','{{').replace('}','}}')})
            
            if question_language.lower() != "english":
                llm_result = await translate_answer(question, question_language, llm_result.content)
                
            return Answer(textResponse=llm_result.content, textExplanation='', data='', label='kb_q') # da rivedere

        # Execute the handler
        context = await handlers[label]()
        #eventually add the log error if user tried to ask for all kpis
        if all_kpis == query_gen.ERROR_NO_KPIS:
            context+="\nError: You can't calculate/predict for no kpis, try again with at least one kpi.\n"
        elif all_kpis == query_gen.ERROR_ALL_KPIS:
            context+="\nError: You can't calculate/predict for all kpis, try again with less kpis.\n"
        if label == 'kb_q':
            # Update the history
            history[userId].append({'question': question.userInput.replace('{','{{').replace('}','}}'), 'answer': context.replace('{','{{').replace('}','}}')})
            
            # Translate the response back to the user's language
            if question_language.lower() != "english":
                context = await translate_answer(question, question_language, context)
                context = context.content

            return Answer(textResponse=context, textExplanation='', data='', label=label)

        # Generate the prompt and invoke the LLM for certain labels
        if label in ['predictions', 'new_kpi', 'report', 'kpi_calc', 'dashboard']:
            # Prepare the history context from previous chat
            history_context = "CONVERSATION HISTORY:\n" + "\n\n".join(
                [f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history[userId]]
            )
            # Prepare the prompt and invoke the LLM
            prompt = prompt_manager.get_prompt(label).format(
                _HISTORY_=history_context,
                _USER_QUERY_=question.userInput,
                _CONTEXT_=context
            )
            
            executor = ThreadPoolExecutor()
            future = executor.submit(llm.invoke, prompt)
            
            if label == 'predictions':
                explainer.add_to_context([("Predictor", "["+context+"]")])

            if label == 'kpi_calc':
                explainer.add_to_context([("KPI Engine", "["+context+"]")])

            if label == 'new_kpi':
                context_cleaned = context.replace("```", "").replace("json\n", "").replace("json", "").replace("```", "")
                explainer.add_to_context([("Knowledge Base", context_cleaned)])

            if label == 'report':
                pred_context, eng_context = context.removeprefix("PRED_CONTEXT:").split("ENG_CONTEXT:")
                pred_context = "["+pred_context+"]"
                eng_context = "["+eng_context+"]"
                explainer.add_to_context([("Predictor", pred_context), ("KPI Engine", eng_context)])

            if label == 'dashboard':
                kb_context, gui_context = context.removeprefix("KB_CONTEXT:").split("GUI_CONTEXT:")
                kb_context = kb_context.replace("```", "").replace("json\n", "").replace("json", "").replace("```", "")
                gui_context = "["+gui_context+"]"
                explainer.add_to_context([("Knowledge Base", kb_context), ("GUI Elements", gui_context)])
            
            llm_result = future.result()
            executor.shutdown(wait=False)
            
            if label in ['predictions', 'report', 'kpi_calc']:
                # Update the history
                history[userId].append({'question': question.userInput.replace('{','{{').replace('}','}}'), 'answer': llm_result.content.replace('{','{{').replace('}','}}')})

                # Translate the response back to thqser's language
                if question_language.lower() != "english":
                    llm_result = await translate_answer(question, question_language, llm_result.content)

            if label == 'predictions':
                textResponse, textExplanation, _ = explainer.attribute_response_to_context(llm_result.content)
                return Answer(textResponse=textResponse, textExplanation=textExplanation, data='', label=label)

            if label == 'kpi_calc':
                textResponse, textExplanation, _ = explainer.attribute_response_to_context(llm_result.content)
                return Answer(textResponse=textResponse, textExplanation=textExplanation, data="", label=label)

            if label == 'new_kpi':                
                response_cleaned = llm_result.content.replace("```", "").replace("json\n", "").replace("json", "").replace("```", "")
                
                if question_language.lower() != "english":
                    history[userId].append({'question': question.userInput.replace('{','{{').replace('}','}}'), 'answer': llm_result.content.replace('{','{{').replace('}','}}')})
                    llm_result = await translate_answer(question, question_language, response_cleaned)
                    textResponse, textExplanation, _ = explainer.attribute_response_to_context(llm_result.content)
                    textResponse = textResponse.replace("```", "").replace("json\n", "").replace("json", "").replace("```", "")
                else:
                    history[userId].append({'question': question.userInput.replace('{','{{').replace('}','}}'), 'answer': llm_result.content.replace('{','{{').replace('}','}}')})
                    textResponse, textExplanation, _ = explainer.attribute_response_to_context(response_cleaned)
                textResponse = textResponse.replace('{', '').replace('}', '').replace('\n\n', '')                
                return Answer(textResponse=textResponse, textExplanation=textExplanation, data=response_cleaned, label=label) 

            if label == 'report':
                textResponse, textExplanation, _ = explainer.attribute_response_to_context(llm_result.content)
                return Answer(textResponse="", textExplanation=textExplanation, data=textResponse, label=label)

            if label == 'dashboard':
                # Converting the JSON string to a dictionary
                response_cleaned = llm_result.content.replace("```", "").replace("json\n", "").replace("json", "").replace("```", "")
                response_json = json.loads(response_cleaned)

                # Update the history
                history[userId].append({'question': question.userInput.replace('{','{{').replace('}','}}'), 'answer': llm_result.content.replace('{','{{').replace('}','}}')})
                            
                if question_language.lower() != "english":
                    llm_result = await translate_answer(question, question_language, response_json["textualResponse"])
                    textResponse, textExplanation, _ = explainer.attribute_response_to_context(llm_result.content)
                else:
                    textResponse, textExplanation, _ = explainer.attribute_response_to_context(response_json["textualResponse"])
                
                data = json.dumps(response_json["bindings"], indent=2)
                return Answer(textResponse=textResponse, textExplanation=textExplanation, data=data, label=label)
    except Exception as e:
        print(e)
        return Answer(textResponse="Something gone wrong, I'm not able to answer your question", textExplanation="", data="", label="Error")