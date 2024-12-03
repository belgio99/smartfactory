# KPI Calculation API

This application provides a KPI calculation engine and an API interface for calculating static and dynamic Key Performance Indicators (KPIs) with customizable filtering options. Users can access the API via browser or HTTP client using a specific URL format. 

## Requirements

Before running the application, ensure the following dependencies are installed:

- **Python** (>=3.8)
- Required libraries:
  - `pandas`
  - `sympy`
  - `uvicorn`
  - `FastAPI`

Install the required libraries using pip:

```bash
pip install pandas sympy uvicorn fastapi
```
## Usage
Start the application using the following command:
```bash
uvicorn main:app --reload
```
This will start the API using environment values, usually on http://0.0.0.0:8000.

### API Access
Access the API endpoint via the following URL format:
```bash
http://0.0.0.0:8000/kpi/{kpiID}/calculate
```
Where {kpiID} is the KPI identifier.
Query parameters can be added to customize filtering.
Query parameters:
  - machineId
  - machineType
  - startPeriod
  - endPeriod
Every query parameter is expected as a string and is optional. By default, the most permissive value will be provided, thus calculating the KPI on all machine, for the whole history of the database.
