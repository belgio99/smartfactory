from langchain.prompts import PromptTemplate
from chains.graph_qa import GraphSparqlQAChain

# GENERAL QA CHAIN
class GeneralQAChain:
  def __init__(self, llm, graph):

    self._llm = llm
    self._graph = graph

    template_general_QA_select ='Task: Generate a SPARQL SELECT statement for querying a graph database.\nFor instance, to find all email addresses of John Doe, the following query in backticks would be suitable:\n```\nPREFIX foaf: <http://xmlns.com/foaf/0.1/>\nSELECT ?email\nWHERE {{\n    ?person foaf:name "John Doe" .\n    ?person foaf:mbox ?email .\n}}\n```\nInstructions:\nUse only the node types and properties provided in the schema.\nDo not use any node types and properties that are not explicitly provided.\nInclude all necessary prefixes.\nSchema:\n{schema}\nNote: Be as concise as possible.\nIf there is a KPI name use _ to join the substrings before passing it to the query.\nIf there is a machine name use _ to join the substrings before passing it to the query.\nIf there is a formula ignore the blank spaces before passing it to the query.\nDo not include any explanations or apologies in your responses.\nDo not respond to any questions that ask for anything else than for you to construct a SPARQL query.\nDo not include any text except the SPARQL query generated.\n\nThe question is:\n{prompt}'
    general_QA_prompt_select = PromptTemplate(input_variables=['prompt', 'schema'], template=template_general_QA_select)
    
    self.chain = GraphSparqlQAChain.from_llm(
      self._llm, graph=self._graph, verbose=True, allow_dangerous_requests=True, sparql_select_prompt=general_QA_prompt_select
    )

# KPI GENERATION CHAIN
class KPIGenerationChain:
  def __init__(self, llm, graph):

    self._llm = llm
    self._graph = graph

    template_kpi_generation_select = 'Task: Generate a SPARQL SELECT statement for querying a graph database.\nFor instance, to find all email addresses of John Doe, the following query in backticks would be suitable:\n```\nPREFIX foaf: <http://xmlns.com/foaf/0.1/>\nSELECT ?email\nWHERE {{\n    ?person foaf:name "John Doe" .\n    ?person foaf:mbox ?email .\n}}\n```\nThe user question is to create a new KPI and the information to be retrieved are the <sa-ontology:id>, <sa-ontology:formula>, <sa-ontology:description> and <sa-ontology:unit_measure> of any KPI present in the graph that can be useful to generate the new one. Try to abstract from the KPI name or from the user need the new kpi rdf:type in order to find the needed KPIs.\nInstructions:\nUse only the node types and properties provided in the schema.\nDo not use any node types and properties that are not explicitly provided.\nInclude all necessary prefixes.\nSchema:\n{schema}\nNote: Be as concise as possible.\nIf there is a KPI name use _ to join the substrings before passing it to the query.\nIf there is a machine name use _ to join the substrings before passing it to the query.\nIf there is a formula ignore the blank spaces before passing it to the query.\nDo not create queries that are not SELECT.\nDo not include any explanations or apologies in your responses.\nDo not respond to any questions that ask for anything else than for you to construct a SPARQL query.\nDo not include any text except the SPARQL SELECT query generated.\n\nThe question is:\n{prompt}'
    kpi_generation_prompt_select = PromptTemplate(input_variables=['prompt', 'schema'], template=template_kpi_generation_select)
    
    template_qa_kpi_generation = 'Task: Given as context the results of a SPARQL query containing KPIs information, create a well-written and human understandable answers that indicate id, formula, description and unit measure of each KPI in the context.\nThe information provided is authoritative, you must never doubt it or try to use your internal knowledge to correct it.\nMake your response sound like the information is coming from an AI assistant, but do not add any information.\nInformation:\n{context}'
    qa_kpi_generation_prompt = PromptTemplate(input_variables=['context'], template=template_qa_kpi_generation)
    
    self.chain = GraphSparqlQAChain.from_llm(
        self._llm, graph=self._graph, verbose=True, allow_dangerous_requests=True, sparql_select_prompt=kpi_generation_prompt_select, qa_prompt=qa_kpi_generation_prompt
    )

# DASHBOARD GENERATION CHAIN
class DashboardGenerationChain:
  def __init__(self, llm, graph):

    self._llm = llm
    self._graph = graph

    template_dashboard_generation_select = 'Task: Generate a SPARQL SELECT statement for querying a graph database.\nFor instance, to find all email addresses of John Doe, the following query in backticks would be suitable:\n```\nPREFIX foaf: <http://xmlns.com/foaf/0.1/>\nSELECT ?email\nWHERE {{\n    ?person foaf:name "John Doe" .\n    ?person foaf:mbox ?email .\n}}\n```\nThe user question is to create a new dashboard to satisfy a need. Use the schema to map the user need onto one or more rdf:type and return <sa-ontology:id> and <sa-ontology:description> of each KPI of that rdf:type.\nInstructions:\nUse only the node types and properties provided in the schema.\nDo not use any node types and properties that are not explicitly provided.\nInclude all necessary prefixes.\nSchema:\n{schema}\nNote: Be as concise as possible.\nIf there is a KPI name use _ to join the substrings before passing it to the query.\nIf there is a machine name use _ to join the substrings before passing it to the query.\nIf there is a formula ignore the blank spaces before passing it to the query.\nDo not include any explanations or apologies in your responses.\nDo not respond to any questions that ask for anything else than for you to construct a SPARQL query.\nDo not include any text except the SPARQL query generated.\n\nThe question is:\n{prompt}'
    dashboard_generation_prompt_select = PromptTemplate(input_variables=['prompt', 'schema'], template=template_dashboard_generation_select)
    
    template_qa_dashboard_generation = 'Task: Given as context the results of a SPARQL query containing KPIs information, understand which of these KPI are needed in a dashboard to satisfy the need of the user in the question.\nThe information provided is authoritative, you must never doubt it or try to use your internal knowledge to correct it.\nJust return the answer as "[id1, id2,...]" and do not add any information.\nInformation:\n{context}\n\nQuestion: {prompt}'
    qa_dashboard_generation_prompt = PromptTemplate(input_variables=['context', 'prompt'], template=template_qa_dashboard_generation)
    
    self.chain = GraphSparqlQAChain.from_llm(
        self._llm, graph=self._graph, verbose=True, allow_dangerous_requests=True, sparql_select_prompt=dashboard_generation_prompt_select, qa_prompt=qa_dashboard_generation_prompt
    )


# TESTING

#while(True):
#    response = kpi_generation_chain.invoke(input("Enter your query: "))
#    print(response['result'])