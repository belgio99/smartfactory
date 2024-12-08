from langchain.prompts import PromptTemplate
from chains.graph_qa import GraphSparqlQAChain

# GENERAL QA CHAIN
class GeneralQAChain:
  def __init__(self, llm, graph, history):

    self._llm = llm
    self._graph = graph

    # Format the history
    history_context = "CONVERSATION HISTORY:\n" + "\n\n".join(
        [f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history]
    )

    template_general_QA_select = history_context + '\n\nTask: Generate a SPARQL SELECT statement for querying a graph database.\nFor instance, to find all information about working time avg KPI, the following query in backticks would be suitable:\n```PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX sa-ontology: <http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#>\n\nSELECT ?description ?formula ?unit_measure ?atomic\nWHERE {{\n?kpi sa-ontology:id "working_time_avg" .\n?kpi sa-ontology:description ?description .\nOPTIONAL {{ ?kpi sa-ontology:formula ?formula }} .\nOPTIONAL {{ ?kpi sa-ontology:unit_measure ?unit_measure }} .\nOPTIONAL {{ ?kpi sa-ontology:atomic ?atomic }} .\n}}```\nInstructions:\nUse only the node types and properties provided in the schema.\nDo not use any node types and properties that are not explicitly provided.\nInclude all necessary prefixes.\nSchema:\n{schema}\nNote: Be as concise as possible.\nIf there is a KPI name use _ to join the substrings before passing it to the query.\nIf there is a machine name use _ to join the substrings before passing it to the query.\nIf there is a formula ignore the blank spaces before passing it to the query.\nIn the WHERE literals use only lowercase letters despite the user input content.\nWhen the user request do not contain an explicit subject, search in the conversation history to find what the user is referring to.\nDo not insert BIND clause in the query.\nDo not include any explanations or apologies in your responses.\nDo not respond to any questions that ask for anything else than for you to construct a SPARQL query.\nDo not include any text except the SPARQL query generated.\n\nThe question is:\n{prompt}'
    general_QA_prompt_select = PromptTemplate(input_variables=['prompt', 'schema'], template=template_general_QA_select)
    
    self.chain = GraphSparqlQAChain.from_llm(
      self._llm, graph=self._graph, verbose=True, allow_dangerous_requests=True, sparql_select_prompt=general_QA_prompt_select
    )

# KPI GENERATION CHAIN
class KPIGenerationChain:
  def __init__(self, llm, graph, history):

    self._llm = llm
    self._graph = graph

    # Format the history
    history_context = "CONVERSATION HISTORY:\n" + "\n\n".join(
        [f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history]
    )

    template_kpi_generation_select = history_context + '\n\nTask: Generate a SPARQL SELECT statement for querying a graph database.\nFor instance, to find all information about working time avg KPI, the following query in backticks would be suitable:\n```PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX sa-ontology: <http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#>\n\nSELECT ?description ?formula ?unit_measure ?atomic\nWHERE {{\n?kpi sa-ontology:id "working_time_avg" .\n?kpi sa-ontology:description ?description .\nOPTIONAL {{ ?kpi sa-ontology:formula ?formula }} .\nOPTIONAL {{ ?kpi sa-ontology:unit_measure ?unit_measure }} .\nOPTIONAL {{ ?kpi sa-ontology:atomic ?atomic }} .\n}}```\nThe user question is to create a new KPI and the information to be retrieved are the <sa-ontology:id>, <sa-ontology:formula>, <sa-ontology:description> and <sa-ontology:unit_measure> of any KPI present in the graph that can be useful to generate the new one. Try to abstract from the KPI name or from the user need the new kpi rdf:type in order to find the needed KPIs.\nInstructions:\nUse only the node types and properties provided in the schema.\nDo not use any node types and properties that are not explicitly provided.\nInclude all necessary prefixes.\nSchema:\n{schema}\nNote: Be as concise as possible.\nIf there is a KPI name use _ to join the substrings before passing it to the query.\nIf there is a machine name use _ to join the substrings before passing it to the query.\nIf there is a formula ignore the blank spaces before passing it to the query.\nDo not create queries that are not SELECT.\nDo not include any explanations or apologies in your responses.\nDo not respond to any questions that ask for anything else than for you to construct a SPARQL query.\nDo not include any text except the SPARQL SELECT query generated.\n\nThe question is:\n{prompt}'
    kpi_generation_prompt_select = PromptTemplate(input_variables=['prompt', 'schema'], template=template_kpi_generation_select)
    
    template_qa_kpi_generation = 'Task: Given as context the results of a SPARQL query containing KPIs information, create a well-written and human understandable answers that indicate id, formula, description and unit measure of each KPI in the context.\nThe information provided is authoritative, you must never doubt it or try to use your internal knowledge to correct it.\nMake your response sound like the information is coming from an AI assistant, but do not add any information.\nInformation:\n{context}'
    qa_kpi_generation_prompt = PromptTemplate(input_variables=['context'], template=template_qa_kpi_generation)
    
    self.chain = GraphSparqlQAChain.from_llm(
        self._llm, graph=self._graph, verbose=True, allow_dangerous_requests=True, sparql_select_prompt=kpi_generation_prompt_select, qa_prompt=qa_kpi_generation_prompt
    )

# DASHBOARD GENERATION CHAIN
class DashboardGenerationChain:
  def __init__(self, llm, graph, history):

    self._llm = llm
    self._graph = graph

    # Format the history
    history_context = "CONVERSATION HISTORY:\n" + "\n\n".join(
        [f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history]
    )

    template_dashboard_generation_select = history_context + '\n\nTask: Generate a SPARQL SELECT statement for querying a graph database.\nFor instance, to find all information about working time avg KPI, the following query in backticks would be suitable:\n```PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX sa-ontology: <http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#>\n\nSELECT ?description ?formula ?unit_measure ?atomic\nWHERE {{\n?kpi sa-ontology:id "working_time_avg" . \n?kpi sa-ontology:description ?description . \n?kpi sa-ontology:formula ?formula .\n?kpi sa-ontology:unit_measure ?unit_measure }} . \n?kpi sa-ontology:atomic ?atomic .\n}}```\nThe user question is to create a new dashboard to satisfy a need. Use the schema to map the user need onto one or more rdf:type. Then return <sa-ontology:id>, <sa-ontology:description>, <sa-ontology:formula> and <sa-ontology:unit_measure> of each KPI of that rdf:type or of a subclass of that rdf:type.\nInstructions:\nUse only the node types and properties provided in the schema.\nDo not use any node types and properties that are not explicitly provided.\nInclude all necessary prefixes.\nSchema:\n{schema}\nNote: Be as concise as possible.\nIf there is a KPI name use _ to join the substrings before passing it to the query.\nIf there is a machine name use _ to join the substrings before passing it to the query.\nIf there is a formula ignore the blank spaces before passing it to the query.\nDo not include any explanations or apologies in your responses.\nDo not respond to any questions that ask for anything else than for you to construct a SPARQL query.\nDo not include any text except the SPARQL query generated.\n\nThe question is:\n{prompt}'
    dashboard_generation_prompt_select = PromptTemplate(input_variables=['prompt', 'schema'], template=template_dashboard_generation_select)
    
    template_qa_dashboard_generation = 'Task: Given as context the results of a SPARQL query containing KPIs information, understand which of these KPI are needed in a dashboard to satisfy the need of the user in the question.\nThe information provided is authoritative, you must never doubt it or try to use your internal knowledge to correct it.\nJust return the answer as an array of JSON object with the following structure "{{ "id": kpi_name, "description": kpi_description, "formula": kpi_formula, "unit_measure": kpi_unit_measure}}" and do not add any information.\nInformation:\n{context}\n\nQuestion: {prompt}'
    qa_dashboard_generation_prompt = PromptTemplate(input_variables=['context', 'prompt'], template=template_qa_dashboard_generation)
    
    self.chain = GraphSparqlQAChain.from_llm(
        self._llm, graph=self._graph, verbose=True, allow_dangerous_requests=True, sparql_select_prompt=dashboard_generation_prompt_select, qa_prompt=qa_dashboard_generation_prompt
    )


# TESTING

#while(True):
#    response = kpi_generation_chain.invoke(input("Enter your query: "))
#    print(response['result'])