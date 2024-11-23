import rdflib
from rdflib.namespace import RDF, Namespace
from owlready2 import *
from fastapi import FastAPI
import json
import sympy


ONTOLOGY_PATH = "../Ontology/sa_ontology.rdf"
onto = get_ontology(ONTOLOGY_PATH).load()
app = FastAPI()

def is_equal(formula1, formula2):
    formula1 = sympy.simplify(sympy.sympify(formula1))
    formula2 = sympy.simplify(sympy.sympify(formula2))

    return formula1 == formula2

def get_kpi(kpi_id):
    query = f'*{kpi_id}'
    a = onto.search(iri = query)
    json_d = {'Status': -1}

    if len(a) == 0:
        return json_d

    for prop in a[0].get_properties():
        for value in prop[a[0]]:
            json_d[prop.name] = value
    
    json_d["Status"] = 0

    return json_d

def extract_datatype_properties(instance):
    """
    Extract datatype properties and their values from an instance.
    """
    datatype_data = {}
    for prop in onto.data_properties():  # Solo datatype properties
        value = prop[instance]  # Recupera il valore della proprietà per l'istanza
        if value:  # Controlla che la proprietà abbia un valore
            datatype_data[prop.name] = value[0]  # Assumiamo un singolo valore per proprietà
    return datatype_data

def get_all_kpis():
    """
    Retrieve all KPIs and their information as dict
    """
    # Recupera tutte le istanze di KPI
    all_kpis = {}
    for kpi in onto.KPI.instances():
        kpi_id = str(kpi.id[0])
        all_kpis[kpi_id] = extract_datatype_properties(kpi)

    return all_kpis

def add_kpi(kpi_info):
    pass

# -------------------------------------------- API Endpoints --------------------------------------------
@app.get("/get_kpi") 
async def get_kpi_endpoint(kpi_id: str):
    """
    Get KPI data by its ID via GET request.
    """
    kpi_data = get_kpi(kpi_id)
    if kpi_data["Status"] == -1:
        return {"error": "KPI not found"}

    return kpi_data

@app.get("/retrieve")
async def get_kpi_endpoint():
    """
    Get KPI data by its ID via GET request.
    """
    kpi_data = get_all_kpis()
    if not kpi_data:
        return {"error": "KPI not found"}
    return kpi_data

if __name__ == "__main__":
    result = get_all_kpis()
    
    print(json.dumps(result, indent=4))