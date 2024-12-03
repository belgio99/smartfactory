# Knowledge Base (KB)

This application serves as a Knowledge Base (KB) and KPI management system, offering an API interface for managing and accessing Key Performance Indicators (KPIs). The KB provides metadata about each KPI and supports integration with systems that produce these KPIs. Users can retrieve detailed KPI information and add new KPIs to the Knowledge Base.

## Requirements

Before running the application, ensure the following dependencies are installed:

- **Python** (>=3.8)
- Required libraries:
  - `owlready2`
  - `sympy`
  - `uvicorn`
  - `FastAPI`

## Install Guide:
Clone the repository:

```bash
git clone -b KB https://github.com/belgio99/smartfactory
cd smartfactory/KB
```

Inside the KB folder run the pip command:

```bash
pip install -r requirements.txt
```

## KPI Info
This is an example of the information for a KPI stored in the Knowledge Base (OWL format):
```xml
<owl:NamedIndividual rdf:about="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#availability">
        <rdf:type rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#Production"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#assembly_machine_1"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#assembly_machine_2"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#assembly_machine_3"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#large_cutting_machine_1"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#large_cutting_machine_2"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#laser_cutter_1"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#laser_welding_machine_1"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#laser_welding_machine_2"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#low_cutting_machine_1"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#medium_cutting_machine_1"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#medium_cutting_machine_2"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#medium_cutting_machine_3"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#riveting_machine_1"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#testing_machine_1"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#testing_machine_2"/>
        <sa-ontology:isProducedBy rdf:resource="http://www.semanticweb.org/raffi/ontologies/2024/10/sa-ontology#testing_machine_3"/>
        <sa-ontology:atomic rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean">true</sa-ontology:atomic>
        <sa-ontology:atomic_formula>availability=working_time_sum/(working_time_sum+idle_time_sum)</sa-ontology:atomic_formula>
        <sa-ontology:description>Percentage of time worked compared to time available.</sa-ontology:description>
        <sa-ontology:forecastable rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean">true</sa-ontology:forecastable>
        <sa-ontology:formula>availability=working_time_sum/(working_time_sum+idle_time_sum)</sa-ontology:formula>
        <sa-ontology:id>availability</sa-ontology:id>
        <sa-ontology:unit_measure>%</sa-ontology:unit_measure>
    </owl:NamedIndividual>
```

## Usage
Start the application using the following command:
```bash
uvicorn main:app --reload
```
This will start the API using environment values, usually on http://127.0.0.1:8000.

### API Access
Access the API endpoint via the following URL format:
```bash
http://127.0.0.1:8000/kpi/{kpiID}/get_kpi
```
Where {kpiID} is the KPI identifier.