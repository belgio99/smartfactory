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
onto = get_ontology(ONTOLOGY_PATH).load() # Load the ontology


def get_kpi(kpi_id):
    """
    Get KPI data by its ID.
    
    Args:
        kpi_id (str): The KPI ID.

    Returns:
        dict: The KPI data.
    """

    query = f'*{kpi_id}'
    results = onto.search(iri = query)
    json_d = {'Status': -1} # default status

    if len(results) == 0:
        return json_d

    for prop in results[0].get_properties():
        for value in prop[results[0]]:
            if isinstance(prop, DataPropertyClass):
                json_d[prop.name] = value
    
    json_d["Status"] = 0 # success status

    return json_d


def get_machine(machine_id):
    """
    Get machine data by its ID.
    
    Args:
        machine_id (str): The machine ID.

    Returns:
        dict: The machine data.
    """

    query = f'*{machine_id}'
    results = onto.search(iri = query)
    json_d = {'Status': -1} # default status

    if len(results) == 0:
        return json_d

    for prop in results[0].get_properties():
        for value in prop[results[0]]:
            if isinstance(prop, DataPropertyClass):
                json_d[prop.name] = value
    
    json_d["Status"] = 0 # success status

    return json_d


def get_all_kpis():
    """
    Retrieve all KPIs and their information as dict

    Returns:
        dict: The KPIs and their information.
    """
 
    all_kpis = {}
    for kpi in onto.KPI.instances():
        kpi_id = str(kpi.id[0])
        all_kpis[kpi_id] = extract_datatype_properties(kpi)
        all_kpis[kpi_id]["type"] = kpi.is_a[0].name

    return all_kpis


def get_all_machines():
    """
    Retrieve all machines and their information as dict

    Returns:
        dict: The machines and their information.
    """

    all_machines = {}
    for machine in onto.Machine.instances():
        machine_id = str(machine.id[0])
        all_machines[machine_id] = extract_datatype_properties(machine)
        all_machines[machine_id]["type"] = machine.is_a[0].name

    return all_machines


def get_classes_hierarchy():
    """
    Organizes the classes in the ontology in a hierarchical structure.

    Returns:
        dict: The classes hierarchy.
    """

    hierarchy = {}

    # Process all classes
    for cls in onto.classes():
        # Get the name of the class
        class_name = cls.name

        if class_name == "Operation" or class_name == "Material" or class_name == "Entity":
            continue

        # Find its subclasses
        subclasses = [subcls.name for subcls in cls.subclasses()]

        # Add the class and its subclasses to the hierarchy
        if class_name not in hierarchy:
            hierarchy[class_name] = []

        for subclass in subclasses:
            if subclass not in hierarchy[class_name]:
                hierarchy[class_name].append(subclass)
    
    def build_tree(node):
        """Recursively build a tree structure for the given node."""
        children = hierarchy.get(node, [])
        return {child: build_tree(child) for child in children}

    # Start with the top-level keys (those not listed as children)
    all_classes = set(hierarchy.keys())
    children_classes = {child for children in hierarchy.values() for child in children}
    top_level_classes = all_classes - children_classes

    # Build the tree starting from the top-level classes
    return {cls: build_tree(cls) for cls in top_level_classes}


def get_kpi_hierarchy():
    """
    Organizes the KPIs in the ontology in a hierarchical structure.

    Returns:
        dict: The KPI hierarchy.
    """
    
    # from get_classes_hierarchy, get only the element inside "KPI"
    kpi_hierarchy = get_classes_hierarchy()["KPI"]
    kpis = get_all_kpis()

    # for each kpi, add the information to the hierarchy (using the type as key)
    for kpi_id, kpi_info in kpis.items():
        kpi_type = kpi_info["type"]
        if kpi_type not in kpi_hierarchy:
            kpi_hierarchy[kpi_type] = {}
        kpi_hierarchy[kpi_type][kpi_id] = kpi_info

    return kpi_hierarchy


def extract_datatype_properties(instance):
    """
    Extract datatype properties and their values from an instance.

    Args:
        instance (Instance): The instance to extract properties from.

    Returns:
        dict: The datatype properties and their values.
    """

    datatype_data = {}
    for prop in onto.data_properties():  # only datatype properties
        value = prop[instance] 
        if value: 
            datatype_data[prop.name] = value[0]  # assume single value
    return datatype_data


def is_pair_machine_kpi_exist(machine_id, kpi_id):
    """
    Check if a pair of machine and KPI exists.

    Args:
        machine_id (str): The machine ID.
        kpi_id (str): The KPI ID.

    Returns:
        dict: The status of the pair. {Status: 0} and the info of the pair if the pair exists, {Status: -1} otherwise.
    """

    json_d = {'Status': -1} # default status

    # Ottieni l'oggetto macchina dall'ontologia
    machine_instance = onto.search_one(id=machine_id)
    if not machine_instance:
        return json_d
    
    # Controlla se il KPI è nella lista dei KPI prodotti dalla macchina
    produces_kpis = [kpi.name for kpi in machine_instance.producesKPI]
    if kpi_id in produces_kpis:
        kpi_tmp = get_kpi(kpi_id)
        json_d["Status"] = 0 # success status
        json_d["machine_id"] = machine_id
        json_d["kpi_id"] = kpi_id
        json_d["unit_measure"] = kpi_tmp["unit_measure"]
        json_d["forecastable"] = kpi_tmp["forecastable"]

    return json_d
    

def is_valid(kpi_info):
    """
    Check if the KPI information is valid.

    Args:
        kpi_info (dict): The KPI information.

    Returns:
        bool: True if the KPI information is valid, False otherwise.
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


# TODO: eliminare perchè non serve più
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

    Returns:
        bool: True if the KPI was added successfully, False otherwise.
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


# TODO: E' da spostare??
def charts_txt(input_file):
    """
    Convert a JSON file with chart descriptions to a formatted TXT file.

    Args:
        input_file (str): Il percorso del file JSON di input.
        output_file (str): Il percorso del file TXT di output.

    Returns:
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





# -------------------------------------------- API Endpoints --------------------------------------------

@app.get("/kb/{kpi_id}/get_kpi") 
async def get_kpi_endpoint(kpi_id: str):
    """
    Get KPI data by its ID via GET request.

    Args:
        kpi_id (str): The KPI ID.

    Returns:
        dict: The KPI data.
    """

    kpi_data = get_kpi(kpi_id)
    if kpi_data["Status"] == -1:
        return {"error": "KPI not found"}

    return kpi_data


@app.get("/kb/retrieve")
async def get_kpi_endpoint():
    """
    Get KPI data by its ID via GET request.

    Args:
        kpi_id (str): The KPI ID.

    Returns:
        dict: The KPI data.
    """

    kpi_data = get_all_kpis()
    if not kpi_data:
        return {"error": "KPI not found"}
    return kpi_data


@app.get("/kb")
def read_root():
    return {"Hello": "World"}





# -------------------------------------------- Main --------------------------------------------

if __name__ == "__main__":
    try:
        tmp = get_kpi_hierarchy()
        with open("kpi_hierarchy.json", "w") as file:
            json.dump(tmp, file, indent=4)
        
        tmp = get_all_kpis()
        for kpi in tmp.items():
            # print index
            print(kpi[0])
  
    except Exception as error:
        print(error)
    
    #uvicorn.run(app, port=8000, host="0.0.0.0")
