from langchain.prompts import PromptTemplate
from chains.graph_qa import GraphSparqlQAChain

# GENERAL QA CHAIN
class GeneralQAChain:
  def __init__(self, llm, graph, history):
    """
    Initializes the GeneralQAChain to handle QA tasks related to graph-based queries.

    Args:
        llm: The language model to generate responses.
        graph: The RDF graph containing the data.
        history: A list of previous conversation entries to inform the context.
    """
    self._llm = llm
    self._graph = graph

    # Format the conversation history into a context string
    history_context = "CONVERSATION HISTORY:\n" + "\n\n".join(
        [f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history]
    )

    template_general_QA_select = history_context + '\n\nTask: Generate a SPARQL SELECT statement for querying a graph database.\nFor instance, to find all information about working time avg KPI, the following query in backticks would be suitable:\n```PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX sa-ontology: <http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#>\n\nSELECT ?description ?formula ?unit_measure ?atomic\nWHERE {{\n?kpi sa-ontology:id "working_time_avg" . \n?kpi sa-ontology:description ?description . \n?kpi sa-ontology:formula ?formula .\n?kpi sa-ontology:unit_measure ?unit_measure }} . \n?kpi sa-ontology:atomic ?atomic .\n}}```. As a second example, to count the number of machines of any type, the following query in backticks would be suitable:\n```PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX sa-ontology: <http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#>\n\nSELECT (COUNT(?machine) AS ?count)\nWHERE {{\n  {{?machine rdf:type sa-ontology:AssemblyMachine .}}\n  UNION\n  {{?machine rdf:type sa-ontology:LargeCapacityCuttingMachine .}}\n  UNION\n  {{?machine rdf:type sa-ontology:LaserCutter .}}\n  UNION\n  {{?machine rdf:type sa-ontology:LaserWeldingMachine .}}\n  UNION\n  {{?machine rdf:type sa-ontology:LowCapacityCuttingMachine .}}\n  UNION\n  {{?machine rdf:type sa-ontology:MediumCapacityCuttingMachine .}}\n  UNION\n  {{?machine rdf:type sa-ontology:RivetingMachine .}}\n  UNION\n  {{?machine rdf:type sa-ontology:TestingMachine .}}\n}}```\nInstructions:\nUse only the node types and properties provided in the schema.\nDo not use any node types and properties that are not explicitly provided.\nInclude all necessary prefixes.\nSchema:\n{schema}\nNote: Be as concise as possible.\nWhen naming a KPI, ensure the following format:\n1. The KPI name must match the one found in <owl:NamedIndividual ...>, such as rdf:about="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#offline_time_avg" for the KPI ID offline_time_avg.\n2. Use lowercase letters for the first letter of each word.\n3. Connect words using underscores (_).\n4. Do not include spaces or special characters.\nExample Format:\n- Correct: offline_time_avg\n- Incorrect: OfflineTimeAvg, offline time avg, or OFFLINE_TIME_AVG.\nAlways follow this convention when naming KPIs.\nWhen generating a machine ID, ensure the following format:\n1. Use uppercase letters for the first letter of each word in the machine name.\n2. Separate each word with a single space.\n3. Include the number as a separate substring at the end, if applicable.\nExample Format:\n- Correct: Assembly Machine 2\n- Incorrect: assemblymachine2, AssemblyMachine2, or assembly machine 2.\nAlways follow this convention when generating machine IDs.\nWhen naming a formula, ensure the following format:\n1. Use the KPI IDs in lowercase, connected by underscores (_).\n2. Use operators (e.g., /, +, -, *) between KPI IDs.\n3. Do not include spaces or special characters, except for the mathematical operators.\nExample Format:\n- Correct: working_time_sum/operative_time\n- Incorrect: WorkingTimeSum/OperativeTime, working_time_sum + operative_time, or working_time_sum operative_time.\nAlways follow this convention when naming formulas.\nDo not include any explanations or apologies in your responses.\nDo not respond to any questions that ask for anything else than for you to construct a SPARQL query.\nDo not include any text except the SPARQL query generated.\nFor the query use only the format SELECT ... WHERE{{...}}.\nGenerate only a single query.\nDo not use FILTER or BIND.\nIf you use the UNION the format of the WHERE clause must be WHERE {{\n     {{\n       ...\n     }} UNION {{\n       ...\n     }}\n   }}\n\nExamples of correct and incorrect formats:\nCorrect:\nWHERE {{\n  {{\n    ... .\n  }} UNION {{\n    ...\n  }}\n}}\n\nIncorrect:\nWHERE {{\n  ... .\n}}\nUNION {{\n  ...\n}}\nIf UNION is outside WHERE, it is invalid, do not generate such queries. This is valid also for KPIs.\nTo correctly match boolean values in SPARQL, use typed literals with the xsd:boolean datatype: "true"^^xsd:boolean \n "false"^^xsd:boolean.\nWhen the user request do not contain an explicit subject, search in the conversation history to find what the user is referring to.\nIf the user request generally talks about machines consider all the rdf:type associated with machines. If the user request generally talks about KPI consider all the rdf:type associated with KPIs \n\nThe question is:\n{prompt}'
    general_QA_prompt_select = PromptTemplate(input_variables=['prompt', 'schema'], template=template_general_QA_select)
    
    template_general_QA_answer="Task: Generate a natural language response from the results of a SPARQL query.\nYou are an assistant that creates well-written and human understandable answers.\nThe information part contains the information provided, which you can use to construct an answer.\nThe information provided is authoritative, you must never doubt it or try to use your internal knowledge to correct it.\nThe information provided is the response from the query, use the query to understand the meaning of the field in the information.\nNote that if a field contains a hyphen, it indicates that the field is not relevant or important in that context, as it does not carry meaningful information. For example, this could occur in a formula within an atomic KPI.\nQuery:\n{query}\n\nInformation:\n{context}\n\nQuestion: {prompt}\nHelpful Answer:"
    general_QA_prompt_answer = PromptTemplate(input_variables=['prompt', 'context', 'query'], template=template_general_QA_answer)

    # Initialize the chain that connects the prompts with the graph-based QA
    self.chain = GraphSparqlQAChain.from_llm(
      self._llm, graph=self._graph, verbose=False, allow_dangerous_requests=True, sparql_select_prompt=general_QA_prompt_select, qa_prompt=general_QA_prompt_answer
    )

# KPI GENERATION CHAIN
class KPIGenerationChain:
  def __init__(self, llm, graph, history):
    """
    Initializes the KPIGenerationChain to generate and query KPIs based on user input.

    Args:
        llm: The language model to generate responses.
        graph: The RDF graph containing the KPI data.
        history: A list of previous conversation entries to inform the context.
    """
    self._llm = llm
    self._graph = graph

    # Format the conversation history into a context string
    history_context = "CONVERSATION HISTORY:\n" + "\n\n".join(
        [f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history]
    )

    template_kpi_generation_select = history_context + '\n\nTask: Generate a SPARQL SELECT statement for querying a graph database.\nFor instance, to find all information about working time avg KPI, the following query in backticks would be suitable:\n```PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX sa-ontology: <http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#>\n\nSELECT ?description ?formula ?unit_measure ?atomic\nWHERE {{\n?kpi sa-ontology:id "working_time_avg" . \n?kpi sa-ontology:description ?description . \n?kpi sa-ontology:formula ?formula .\n?kpi sa-ontology:unit_measure ?unit_measure }} . \n?kpi sa-ontology:atomic ?atomic .\n}}```\nThe user question is to create a new KPI and the information to be retrieved are the <sa-ontology:id>, <sa-ontology:formula>, <sa-ontology:description> and <sa-ontology:unit_measure> of any KPI present in the graph that can be useful to generate the new one. Try to abstract from the KPI name or from the user need the new kpi rdf:type in order to find the needed KPIs.\nInstructions:\nUse only the node types and properties provided in the schema.\nDo not use any node types and properties that are not explicitly provided.\nInclude all necessary prefixes.\nSchema:\n{schema}\nNote: Be as concise as possible.\nWhen naming a KPI, ensure the following format:\n1. The KPI name must match the one found in <owl:NamedIndividual ...>, such as rdf:about="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#offline_time_avg" for the KPI ID offline_time_avg.\n2. Use lowercase letters for the first letter of each word.\n3. Connect words using underscores (_).\n4. Do not include spaces or special characters.\nExample Format:\n- Correct: offline_time_avg\n- Incorrect: OfflineTimeAvg, offline time avg, or OFFLINE_TIME_AVG.\nAlways follow this convention when naming KPIs.\nWhen generating a machine ID, ensure the following format:\n1. Use uppercase letters for the first letter of each word in the machine name.\n2. Separate each word with a single space.\n3. Include the number as a separate substring at the end, if applicable.\nExample Format:\n- Correct: Assembly Machine 2\n- Incorrect: assemblymachine2, AssemblyMachine2, or assembly machine 2.\nAlways follow this convention when generating machine IDs.\nWhen naming a formula, ensure the following format:\n1. Use the KPI IDs in lowercase, connected by underscores (_).\n2. Use operators (e.g., /, +, -, *) between KPI IDs.\n3. Do not include spaces or special characters, except for the mathematical operators.\nExample Format:\n- Correct: working_time_sum/operative_time\n- Incorrect: WorkingTimeSum/OperativeTime, working_time_sum + operative_time, or working_time_sum operative_time.\nAlways follow this convention when naming formulas.\nDo not include any explanations or apologies in your responses.\nDo not respond to any questions that ask for anything else than for you to construct a SPARQL query.\nDo not include any text except the SPARQL query generated.\nFor the query use only the format SELECT ... WHERE{{...}}.\n Do not use UNION, FILTER or BIND.\n\nThe question is:\n{prompt}'
    kpi_generation_prompt_select = PromptTemplate(input_variables=['prompt', 'schema'], template=template_kpi_generation_select)
    
    template_qa_kpi_generation = 'Task: Given as context the results of a SPARQL query containing KPIs information, create a answers that indicate id, formula, description and unit measure of each KPI in the context.\nThe information provided is authoritative, you must never doubt it or try to use your internal knowledge to correct it.\nJust return the answer as an array of JSON object with the following structure "{{ "id": kpi_name, "description": kpi_description, "formula": kpi_formula, "unit_measure": kpi_unit_measure}}" and do not add any information.\nInformation:\n{context}'
    qa_kpi_generation_prompt = PromptTemplate(input_variables=['context'], template=template_qa_kpi_generation)
    
    # Initialize the chain that connects the prompts with KPI generation
    self.chain = GraphSparqlQAChain.from_llm(
        self._llm, graph=self._graph, verbose=False, allow_dangerous_requests=True, sparql_select_prompt=kpi_generation_prompt_select, qa_prompt=qa_kpi_generation_prompt
    )

# DASHBOARD GENERATION CHAIN
class DashboardGenerationChain:
  def __init__(self, llm, graph, history):
    """
    Initializes the DashboardGenerationChain to generate and query dashboards based on user input.

    Args:
        llm: The language model to generate responses.
        graph: The RDF graph containing the KPI and dashboard data.
        history: A list of previous conversation entries to inform the context.
    """
    self._llm = llm
    self._graph = graph

    # Format the conversation history into a context string
    history_context = "CONVERSATION HISTORY:\n" + "\n\n".join(
        [f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history]
    )

    template_dashboard_generation_select = history_context + '\n\nTask: Generate a SPARQL SELECT statement for querying a graph database.\nFor instance, to find all information about working time avg KPI, the following query in backticks would be suitable:\n```PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX sa-ontology: <http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#>\n\nSELECT ?description ?formula ?unit_measure ?atomic\nWHERE {{\n?kpi sa-ontology:id "working_time_avg" . \n?kpi sa-ontology:description ?description . \n?kpi sa-ontology:formula ?formula .\n?kpi sa-ontology:unit_measure ?unit_measure }} . \n?kpi sa-ontology:atomic ?atomic .\n}}```\nThe user question is to create a new dashboard to satisfy a need. Use the schema to map the user need onto one or more rdf:type. Then return <sa-ontology:id>, <sa-ontology:description>, <sa-ontology:formula> and <sa-ontology:unit_measure> of each KPI of that rdf:type.\nInstructions:\nUse only the node types and properties provided in the schema.\nDo not use any node types and properties that are not explicitly provided.\nInclude all necessary prefixes.\nSchema:\n{schema}\nNote: Be as concise as possible.\nWhen naming a KPI, ensure the following format:\n1. The KPI name must match the one found in <owl:NamedIndividual ...>, such as rdf:about="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#offline_time_avg" for the KPI ID offline_time_avg.\n2. Use lowercase letters for the first letter of each word.\n3. Connect words using underscores (_).\n4. Do not include spaces or special characters.\nExample Format:\n- Correct: offline_time_avg\n- Incorrect: OfflineTimeAvg, offline time avg, or OFFLINE_TIME_AVG.\nAlways follow this convention when naming KPIs.\nWhen generating a machine ID, ensure the following format:\n1. Use uppercase letters for the first letter of each word in the machine name.\n2. Separate each word with a single space.\n3. Include the number as a separate substring at the end, if applicable.\nExample Format:\n- Correct: Assembly Machine 2\n- Incorrect: assemblymachine2, AssemblyMachine2, or assembly machine 2.\nAlways follow this convention when generating machine IDs.\nWhen naming a formula, ensure the following format:\n1. Use the KPI IDs in lowercase, connected by underscores (_).\n2. Use operators (e.g., /, +, -, *) between KPI IDs.\n3. Do not include spaces or special characters, except for the mathematical operators.\nExample Format:\n- Correct: working_time_sum/operative_time\n- Incorrect: WorkingTimeSum/OperativeTime, working_time_sum + operative_time, or working_time_sum operative_time.\nAlways follow this convention when naming formulas.\nDo not include any explanations or apologies in your responses.\nDo not respond to any questions that ask for anything else than for you to construct a SPARQL query.\nDo not include any text except the SPARQL query generated.\nFor the query use only the format SELECT ... WHERE{{...}}.\nDo not use UNION, FILTER or BIND.\n\nThe question is:\n{prompt}'
    dashboard_generation_prompt_select = PromptTemplate(input_variables=['prompt', 'schema'], template=template_dashboard_generation_select)
    
    template_qa_dashboard_generation = 'Task: Given as context the results of a SPARQL query containing KPIs information, understand which of these KPI are needed in a dashboard to satisfy the need of the user in the question.\nThe information provided is authoritative, you must never doubt it or try to use your internal knowledge to correct it.\nJust return the answer as an array of JSON object with the following structure "{{ "id": kpi_name, "description": kpi_description, "formula": kpi_formula, "unit_measure": kpi_unit_measure}}" and do not add any information.\nInformation:\n{context}\n\nQuestion: {prompt}'
    qa_dashboard_generation_prompt = PromptTemplate(input_variables=['context', 'prompt'], template=template_qa_dashboard_generation)
    
    # Initialize the chain that connects the prompts with dashboard generation
    self.chain = GraphSparqlQAChain.from_llm(
        self._llm, graph=self._graph, verbose=False, allow_dangerous_requests=True, sparql_select_prompt=dashboard_generation_prompt_select, qa_prompt=qa_dashboard_generation_prompt
    )