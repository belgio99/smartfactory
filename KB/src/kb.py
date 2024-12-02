from owlready2 import *
import sympy

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


ONTOLOGY_PATH = "./Ontology/sa_ontology.rdf"
TMP_ONTOLOGY_PATH = "./Ontology/tmp_ontology.rdf"
onto = get_ontology(ONTOLOGY_PATH).load()


def get_kpi(kpi_id):
    """
    Get KPI data by its ID.
    
    Args:
        kpi_id (str): The KPI ID.
    """

    query = f'*{kpi_id}'
    results = onto.search(iri = query)
    json_d = {'Status': -1}

    if len(results) == 0:
        return json_d

    for prop in results[0].get_properties():
        for value in prop[results[0]]:
            if isinstance(prop, DataPropertyClass):
                json_d[prop.name] = value
    
    json_d["Status"] = 0

    return json_d


def get_all_kpis():
    """
    Retrieve all KPIs and their information as dict
    """
 
    all_kpis = {}
    for kpi in onto.KPI.instances():
        kpi_id = str(kpi.id[0])
        all_kpis[kpi_id] = extract_datatype_properties(kpi)
        # add type of KPI given the class
        #all_kpis[kpi_id]["type"] = 

    return all_kpis


def get_all_machines():
    """
    Retrieve all machines and their information as dict
    """

    all_machines = {}
    for machine in onto.Machine.instances():
        machine_id = str(machine.id[0])
        all_machines[machine_id] = extract_datatype_properties(machine)

    return all_machines


def extract_datatype_properties(instance):
    """
    Extract datatype properties and their values from an instance.
    """

    datatype_data = {}
    for prop in onto.data_properties():  # only datatype properties
        value = prop[instance] 
        if value: 
            datatype_data[prop.name] = value[0]  # assume single value
    return datatype_data


def get_atomic_formula(kpi_id):
    """
    Get the atomic formula of a KPI by its ID.

    Args:
        kpi_id (str): The KPI ID.
    """

    kpi = get_kpi(kpi_id)
    if kpi["Status"] == -1:
        return None
    else:
        return kpi["atomic_formula"]
    

def get_unit_measure(kpi_id):
    """
    Get the unit measure of a KPI by its ID.

    Args:
        kpi_id (str): The KPI ID.
    """

    kpi = get_kpi(kpi_id)
    if kpi["Status"] == -1:
        return None
    else:
        return kpi["unit_measure"]


def get_all_kpi_unit():
    """
    Retrieve all KPIs and their unit measures as dict
    """
 
    all_kpis = {}
    for kpi in onto.KPI.instances():
        kpi_id = str(kpi.id[0])
        all_kpis[kpi_id] = kpi.unit_measure[0]

 
    all_kpis = []
    for kpi in onto.KPI.instances():
        kpi_entry = {
            "kpi": str(kpi.id[0]),
            "unit": kpi.unit_measure[0]
        }
        all_kpis.append(kpi_entry)

    return all_kpis


def get_all_machine_kpi():
    """
    Retrieve all machines and their KPIs as a list of dicts in the specified format.
    """

    all_machines = []
    
    # Itera su tutte le istanze di macchine nell'ontologia
    for machine in onto.search(type=onto.Machine):
        # Recupera l'ID della macchina
        machine_id = machine.id[0] if machine.id else str(machine.name)
        
        # Recupera i KPI associati utilizzando la proprietà producesKPI
        kpis = []
        for kpi in machine.producesKPI:
            kpis.append(kpi.name)  # Nome del KPI associato
        
        # Crea il dizionario per la macchina e i suoi KPI
        machine_entry = {
            "machine": machine_id,
            "kpi": kpis
        }
        all_machines.append(machine_entry)
    
    return all_machines



def is_valid(kpi_info):
    """
    Check if the KPI information is valid.

    Args:
        kpi_info (dict): The KPI information.
    """

    def is_equal(formula1, formula2):
        formula1 = sympy.simplify(sympy.sympify(formula1))
        formula2 = sympy.simplify(sympy.sympify(formula2))

        return formula1 == formula2
    
    formula = kpi_info['atomic_formula'][0]

    for kpi in onto.KPI.instances():
        if kpi.formula[0] != '-' and formula != '-':
            if is_equal(kpi.atomic_formula[0], formula):
                return False
            
    return True


def rdf_to_txt(onto, output_file):
    """
    Convert an ontology to a formatted TXT file.

    Args:
        onto (Ontology): The ontology to convert.
        output_file (str): The path of the output TXT file.
    """

    def write_class_hierarchy(file, cls, indent=0):
        """
        Funzione ricorsiva per scrivere la gerarchia delle classi, comprese le sottoclassi.
        """
        file.write("  " * indent + f"Class: {cls.name}\n")
        
        for subclass in cls.subclasses():
            write_class_hierarchy(file, subclass, indent + 1)
    
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("Classes:\n")
        for cls in onto.classes():
            if cls != Thing:
                write_class_hierarchy(file, cls)

        file.write("\nProperties:\n")
        for prop in onto.properties():
            file.write(f"Property: {prop.name}\n")
            
            if isinstance(prop, ObjectPropertyClass):
                domain = prop.domain
                range_ = prop.range
                file.write(f"  Type: ObjectProperty\n")
                file.write(f"  Domain: {domain[0].name}\n")
                file.write(f"  Range: {range_[0].name}\n")
            elif isinstance(prop, DataPropertyClass):
                data_type = prop.range
                file.write(f"  Type: DataProperty\n")
                file.write(f"  Data Type: {data_type[0].__name__}\n")
            elif isinstance(prop, AnnotationPropertyClass):
                file.write("  Type: AnnotationProperty\n")

        file.write("\nIndividuals:\n")
        for individual in onto.individuals():
            file.write(f"Individual: {individual.name}\n")
            
            for prop in individual.get_properties():
                values = prop[individual]
                for value in values:
                   
                    if isinstance(value, Thing): 
                        file.write(f"  {prop.name}: {value.name}\n")
                    else: 
                        file.write(f"  {prop.name}: {value}\n")
            file.write("\n")


def add_kpi(kpi_info):
    """
    Add a new KPI to the ontology.

    Args:
        kpi_info (dict): The KPI information.
    """

    if not is_valid(kpi_info):
        return False
    
    custom_class = onto.CustomKPItmp
    new_kpi = custom_class(kpi_info['id'][0], id=kpi_info['id'], description=kpi_info['description'], 
                           atomic_formula=kpi_info['atomic_formula'], formula=kpi_info['formula'], 
                           unit_measure=kpi_info['unit_measure'], forecastable=kpi_info['forecastable'], atomic=kpi_info['atomic'])
    
    with onto:
        try:
            sync_reasoner()
            onto.save(file = TMP_ONTOLOGY_PATH, format = "rdfxml")
        except Exception as error:
            return False
    
    return True


def charts_txt(input_file):
    """
    Convert a JSON file with chart descriptions to a formatted TXT file.

    Args:
        input_file (str): Il percorso del file JSON di input.
        output_file (str): Il percorso del file TXT di output.
    """
    
    # Load the JSON file
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    """# Convert the JSON to the required format and write to the output file
    with open(output_file, 'w', encoding='utf-8') as output:
        for entry in data:
            output.write(f"chart: {entry['chart']}\n")
            output.write(f"description: {entry['description']}\n\n")

    print(f"Conversion completed")"""

    # Convert the JSON to the required format and return it as a string
    result = ""
    for entry in data:
        result += f"chart: {entry['chart']}\n"
        result += f"description: {entry['description']}\n\n"

    print(f"Conversion completed")
    
    return result


if __name__ == "__main__":
    """try:
        sync_reasoner()
        print("test reasoner")
    except Exception as error:
        print(error)"""

# -------------------------------------------- API Endpoints --------------------------------------------

@app.get("/kb/{kpi_id}/get_kpi") 
async def get_kpi_endpoint(kpi_id: str):
    """
    Get KPI data by its ID via GET request.
    """
    kpi_data = get_kpi(kpi_id)
    if kpi_data["Status"] == -1:
        return {"error": "KPI not found"}

    return kpi_data


@app.get("/kb/retrieve")
async def get_kpi_endpoint():
    """
    Get KPI data by its ID via GET request.
    """
    kpi_data = get_all_kpis()
    if not kpi_data:
        return {"error": "KPI not found"}
    return kpi_data


@app.get("/kb")
def read_root():
    return {"Hello": "World"}