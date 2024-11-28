import rdflib
from rdflib.namespace import RDF, Namespace
import json
import sympy

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


ONTOLOGY_PATH = "./Ontology/sa_ontology.rdf"
SA = Namespace("http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#")
g = rdflib.Graph()
g.parse(ONTOLOGY_PATH)

def rdf_to_json(rdf_kpi):
    kpi_data = {}

    # Iterate over the results and format them as {property: value}
    for row in rdf_kpi:
        property_uri = str(row.property)  # Property as a URI string
        value = str(row.value)  # Value as a string
        
        # Extract the property name (e.g., `unit_measure` from the full URI)
        property_name = property_uri.split('#')[-1]
        
        # Add to dictionary
        kpi_data[property_name] = value

    return kpi_data

def get_kpi(kpi_id):
    # Query the RDF graph for the single KPI data
    query = f""" 
    PREFIX sa: <http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?property ?value ?datatype
    WHERE {{
        ?kpi sa:id "{kpi_id}" ;
             ?property ?value .
        # Ensure we are dealing with literal values
        FILTER(isLiteral(?value))
        # Match the datatype URI embedded in the literal value
        BIND(datatype(?value) AS ?datatype)
    }}
    """

    results = g.query(query)

    return rdf_to_json(results) # Convert RDF results to JSON format

def is_equal(formula1, formula2):
    formula1 = sympy.simplify(sympy.sympify(formula1))
    formula2 = sympy.simplify(sympy.sympify(formula2))

    return formula1 == formula2

@app.get("/kb/{kpi_id}/get_kpi")
async def get_kpi_endpoint(kpi_id: str):
    """
    Get KPI data by its ID via GET request.
    """
    kpi_data = get_kpi(kpi_id)
    if not kpi_data:
        return {"error": "KPI not found"}
    return kpi_data

@app.get("/kb")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    result = get_kpi("operative_time")

    #uvicorn.run(app, port=8000, host="0.0.0.0")