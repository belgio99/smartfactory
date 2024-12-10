"""
@file kb.py
@brief This file contains the implementation of the KB.
@author Nicola Emmolo, Jacopo Raffi
"""

from owlready2 import *
import sympy
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
import json
from api_auth.api_auth import get_verify_api_key
from pydantic import BaseModel
import shutil


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ONTOLOGY_PATH = "./storage/sa_ontology.rdf"
onto = None


def get_kpi(kpi_id):
    """
    Retrieve KPI data by its ID.

    This function queries an ontology to retrieve KPI data using the given KPI ID.
    If no data is found, it returns a default response with "Status" set to -1.

    Args:
        kpi_id (str): The unique identifier of the machine.

    Globals:
        onto (Ontology): The global ontology object is used to extract KPIs.

    Returns: 
        dict A dictionary containing the KPI data. The structure includes:
            - "Status" (int): 0 if successful, -1 if no machine data is found.
            - Additional keys corresponding to the KPI's data properties.
    """

    query = f'*#{kpi_id}'
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
    Retrieve machine data by its ID.

    This function queries an ontology to retrieve machine data using the given machine ID.
    If no data is found, it returns a default response with "Status" set to -1.

    Args:
        machine_id (str): The unique identifier of the machine.

    Globals:
        onto (Ontology): The global ontology object is used to extract machines.

    Returns:
        dict: A dictionary containing the machine data. The structure includes:
            - "Status" (int): 0 if successful, -1 if no machine data is found.
            - Additional keys corresponding to the machine's data properties.
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

    Globals:
        onto (Ontology): The global ontology object is used to extract KPIs.

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

    Globals:
        onto (Ontology): The global ontology object is used to extract machines.

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

    Globals:
        onto (Ontology): The global ontology object is used to extract classes.

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
    Organizes the KPIs directly under the main classes of the ontology, removes empty classes, 
    and updates the 'type' of each KPI to match its main class.

    Returns:
        dict: The list of KPIs, grouped under the main classes of the ontology.
    """

    def find_main_class_for_kpi(main_class_hierarchy, kpi_type):
        """
        Recursively finds if a KPI type exists in the hierarchy of a main class.

        Args:
            main_class_hierarchy (dict): The hierarchy of the main class.
            kpi_type (str): The type of the KPI.

        Returns:
            bool: True if the KPI type is found, False otherwise.
        """
        for key, value in main_class_hierarchy.items():
            if key == kpi_type:
                return True
            if isinstance(value, dict):  # Recursively check sub-hierarchy
                if find_main_class_for_kpi(value, kpi_type):
                    return True
        return False

    def remove_empty_classes(hierarchy):
        """
        Recursively removes empty classes from the hierarchy.

        Args:
            hierarchy (dict): The hierarchy to clean.

        Returns:
            dict: The cleaned hierarchy without empty classes.
        """
        cleaned_hierarchy = {}
        for key, value in hierarchy.items():
            if isinstance(value, dict):
                # Recursively clean sub-hierarchy
                nested = remove_empty_classes(value)
                if nested:  # Only include non-empty classes
                    cleaned_hierarchy[key] = nested
            elif value:  # Include non-dict non-empty values
                cleaned_hierarchy[key] = value
        return cleaned_hierarchy

    # Retrieve the initial hierarchy and the list of KPIs
    full_hierarchy = get_classes_hierarchy().get("KPI", {})
    main_classes = list(full_hierarchy.keys())  # Extract only the main classes
    kpis = get_all_kpis()

    # Create a simplified hierarchy initialized with the main classes
    simplified_hierarchy = {main_class: {} for main_class in main_classes}

    # Insert each KPI under the corresponding main class
    for kpi_id, kpi_info in kpis.items():
        kpi_type = kpi_info["type"]

        # Check if the KPI type matches exactly a main class
        if kpi_type in main_classes:
            kpi_info["type"] = kpi_type  # Update type to the main class name
            simplified_hierarchy[kpi_type][kpi_id] = kpi_info
            continue

        # Find the main class that contains the KPI type
        for main_class in main_classes:
            if find_main_class_for_kpi(full_hierarchy[main_class], kpi_type):
                kpi_info["type"] = main_class  # Update type to the main class name
                simplified_hierarchy[main_class][kpi_id] = kpi_info
                break
        else:
            # If the type is not associated with any main class, raise an error
            raise ValueError(f"Unable to classify KPI {kpi_id} with type {kpi_type} under any main class.")

    # Remove empty classes from the hierarchy
    return remove_empty_classes(simplified_hierarchy)


def get_machine_hierarchy():
    """
    Organizes the machines directly under the main classes of the ontology, removes empty classes,
    and updates the 'type' of each machine to match its main class.

    Returns:
        dict: The list of machines, grouped under the main classes of the ontology.
    """

    def find_main_class_for_machine(main_class_hierarchy, machine_type):
        """
        Recursively finds if a machine type exists in the hierarchy of a main class.

        Args:
            main_class_hierarchy (dict): The hierarchy of the main class.
            machine_type (str): The type of the machine.

        Returns:
            bool: True if the machine type is found, False otherwise.
        """
        for key, value in main_class_hierarchy.items():
            if key == machine_type:
                return True
            if isinstance(value, dict):  # Recursively check sub-hierarchy
                if find_main_class_for_machine(value, machine_type):
                    return True
        return False

    def remove_empty_classes(hierarchy):
        """
        Recursively removes empty classes from the hierarchy.

        Args:
            hierarchy (dict): The hierarchy to clean.

        Returns:
            dict: The cleaned hierarchy without empty classes.
        """
        cleaned_hierarchy = {}
        for key, value in hierarchy.items():
            if isinstance(value, dict):
                # Recursively clean sub-hierarchy
                nested = remove_empty_classes(value)
                if nested:  # Only include non-empty classes
                    cleaned_hierarchy[key] = nested
            elif value:  # Include non-dict non-empty values
                cleaned_hierarchy[key] = value
        return cleaned_hierarchy

    # Retrieve the initial hierarchy and the list of machines
    full_hierarchy = get_classes_hierarchy().get("Machine", {})
    main_classes = list(full_hierarchy.keys())  # Extract only the main classes
    machines = get_all_machines()

    # Create a simplified hierarchy initialized with the main classes
    simplified_hierarchy = {main_class: {} for main_class in main_classes}

    # Insert each machine under the corresponding main class
    for machine_id, machine_info in machines.items():
        machine_type = machine_info["type"]

        # Check if the machine type matches exactly a main class
        if machine_type in main_classes:
            machine_info["type"] = machine_type  # Update type to the main class name
            simplified_hierarchy[machine_type][machine_id] = machine_info
            continue

        # Find the main class that contains the machine type
        for main_class in main_classes:
            if find_main_class_for_machine(full_hierarchy[main_class], machine_type):
                machine_info["type"] = main_class  # Update type to the main class name
                simplified_hierarchy[main_class][machine_id] = machine_info
                break
        else:
            # If the type is not associated with any main class, raise an error
            raise ValueError(f"Unable to classify machine {machine_id} with type {machine_type} under any main class.")

    # Remove empty classes from the hierarchy
    return remove_empty_classes(simplified_hierarchy)



def extract_datatype_properties(instance):
    """
    Extract datatype properties and their values from an instance.

    Args:
        instance (Instance): The instance to extract properties from.

    Globals:
        onto (Ontology): The global ontology object is used to extract properties.

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

    Globals:
        onto (Ontology): The global ontology object is used to check the pair.

    Returns:
        dict: The status of the pair. {Status: 0} and the info of the pair if the pair exists, {Status: -1} otherwise.
    """

    query = f'*{machine_id.lower().replace(" ", "_")}'
    result = onto.search_one(iri = query)
    json_d = {'Status': -1} # default status

    if not result: # machine not found
        return json_d
    
    # Check if the KPI is in the list of KPIs produced by the machine
    produces_kpis = [kpi.name for kpi in result.producesKPI]
    if kpi_id in produces_kpis: # kpi found
        kpi_tmp = get_kpi(kpi_id)
        json_d["Status"] = 0 # success status
        json_d["machine_id"] = machine_id
        json_d["kpi_id"] = kpi_id
        json_d["unit_measure"] = kpi_tmp["unit_measure"]
        json_d["forecastable"] = kpi_tmp["forecastable"]

    return json_d
    

def is_valid(kpi_info):
    """
    Check if the KPI has the same formula of other KPIs.

    Args:
        kpi_info (dict): The KPI information.

    Globals:
        onto (Ontology): The global ontology object is used to check the KPIs.

    Returns:
        bool: True if there is at least 1 KPI with the same atomic_formula, False otherwise.
    """

    def is_equal(formula1, formula2):
        """
        Check if two formulas are equal.

        Args:
            formula1 (str): The first formula.
            formula2 (str): The second formula.

        Returns:
            bool: True if the formulas are equal, False otherwise
        """
        formula1 = sympy.simplify(sympy.sympify(formula1))
        formula2 = sympy.simplify(sympy.sympify(formula2))

        return formula1 == formula2
    
    formula = kpi_info['atomic_formula'][0]

    for kpi in onto.KPI.instances():
        if kpi.formula[0] != '-' and formula != '-':
            if is_equal(kpi.atomic_formula[0], formula):
                return False
            
    return True


def reduce_formula(formula):
    '''
    Reduce a formula to its simplest form (with only atomic KPIs).

    Args:
        formula (str): The formula to reduce.    
    
    Returns:
        str: The reduced formula. None if a KPI in the formula is not found.
    '''

    formula = sympy.sympify(formula)

    symbols_in_formula = formula.free_symbols

    for symbol in symbols_in_formula:
        str_symbol = str(symbol)
        kpi = get_kpi(str_symbol)

        if kpi["Status"] == -1:
            return None
        
        if kpi["atomic"] == False: # if the KPI is not atomic substitute it with its formula
            formula = formula.subs(symbol, sympy.sympify(kpi["atomic_formula"]))
    
    return str(formula)


def add_kpi(kpi_info):
    """
    Add a KPI to the ontology.

    This function modifies the global ontology state by adding a new KPI (Key Performance Indicator) 
    to the relevant entities.

    Args:
        kpi_info (dict): The information of the KPI to add.

    Globals:
        onto (Ontology): The global ontology object is modified to include the new KPI.

    Returns:
        bool: True if the KPI was successfully added, False otherwise.

    Raises:
        ValueError: If the Hermit reasoner finds problems with the KPI.
    """

    with onto:
        try:
            atomic_formula = reduce_formula(kpi_info["formula"][0])
            kpi_info["atomic_formula"] = [atomic_formula]

            if not is_valid(kpi_info):
                return False
            
            if atomic_formula is None:
                return False
            
            custom_class = onto.CustomKPItmp
            machines = onto.Machine.instances()
            new_kpi = custom_class(kpi_info['id'][0], id=kpi_info['id'], description=kpi_info['description'], 
                                atomic_formula=kpi_info['atomic_formula'], formula=kpi_info['formula'], 
                                unit_measure=kpi_info['unit_measure'], forecastable=kpi_info['forecastable'], atomic=kpi_info['atomic'], isProducedBy=machines)
            
            for machine in onto.Machine.instances():  # Iterates over all instances of 'Machine'
                # Here you might want to apply a condition to select which machines should produce this KPI
                machine.producesKPI.append(new_kpi)

            sync_reasoner()
            onto.save(file = ONTOLOGY_PATH, format = "rdfxml")
        except Exception as error:
            print(error)
            return False
        
        return True





# -------------------------------------------- API Endpoints --------------------------------------------

@app.get("/kb/{kpi_id}/get_kpi") 
async def get_kpi_endpoint(kpi_id: str, api_key: str = Depends(get_verify_api_key(["kpi-engine"]))): # to add or modify the services allowed to access the API, add or remove them from the list in the get_verify_api_key function e.g. get_verify_api_key(["gui", "service1", "service2"])
    """
    Get KPI data by its ID via GET request.

    Args:
        kpi_id (str): The KPI ID.

    Returns:
        dict: The KPI data.
    """

    kpi_data = get_kpi(kpi_id)
    return kpi_data


@app.get("/kb/retrieveKPIs")
async def get_all_kpis_endpoint(api_key: str = Depends(get_verify_api_key(["api-layer", "ai-agent"]))): # to add or modify the services allowed to access the API, add or remove them from the list in the get_verify_api_key function e.g. get_verify_api_key(["gui", "service1", "service2"])
    """
    Get all KPIs, grouped under the main classes of the ontology

    Returns:
        dict: The KPIs and their information.
    """

    kpi_data = get_kpi_hierarchy()
    return kpi_data


@app.get("/kb/retrieveMachines")
async def get_all_machines_endpoint(api_key: str = Depends(get_verify_api_key(["gui"]))): # to add or modify the services allowed to access the API, add or remove them from the list in the get_verify_api_key function e.g. get_verify_api_key(["gui", "service1", "service2"])
    """
    Get all machines, grouped under the main classes of the ontology

    Returns:
        dict: The machines and their information.
    """

    machines_data = get_machine_hierarchy()
    return machines_data


@app.get("/kb/{machine_id}/{kpi_id}/check")
async def is_pair_machine_kpi_exist_endpoint(machine_id: str, kpi_id: str, api_key: str = Depends(get_verify_api_key(["data"]))): # to add or modify the services allowed to access the API, add or remove them from the list in the get_verify_api_key function e.g. get_verify_api_key(["gui", "service1", "service2"])
    """
    Check if a pair of machine and KPI exists via GET request.

    Args:
        machine_id (str): The machine ID.
        kpi_id (str): The KPI ID.

    Returns:
        dict: The status of the pair, and the info of the pair if the pair exists.
    """

    pair_status = is_pair_machine_kpi_exist(machine_id, kpi_id)
    return pair_status


class KPI_Info(BaseModel):
    id: str
    description: str
    formula: str
    unit_measure: str
    forecastable: bool
    atomic: bool

@app.post("/kb/insert")
async def add_kpi_endpoint(kpi_info: KPI_Info):
    """
    Add a KPI to the ontology

    Args:
        kpi_info (KPI_Info): The information of the KPI to add.

    Returns:
        dict: The status of the operation.
    """

    kpi_info_dict = {
        "id": [kpi_info.id],
        "description": [kpi_info.description],
        "formula": [kpi_info.formula],
        "unit_measure": [kpi_info.unit_measure],
        "forecastable": [kpi_info.forecastable],
        "atomic": [kpi_info.atomic],
    }

    result = add_kpi(kpi_info_dict)
    if not result:
        return {"Status": -1, "message": "KPI not added"}
    return {"Status": 0, "message": "KPI added"}





# -------------------------------------------- Main --------------------------------------------

if __name__ == "__main__":
    # check if the "storage" folder is empty ("./storage")
    if not os.listdir("./storage"):
        # insert ontology file ("./Ontology/sa_ontology.rdf") in the "storage" folder
        shutil.copyfile("./Ontology/sa_ontology.rdf", "./storage/sa_ontology.rdf")

    onto = get_ontology(ONTOLOGY_PATH).load() # Load the ontology

    uvicorn.run(app, port=8000, host="0.0.0.0")
