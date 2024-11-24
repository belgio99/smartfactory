## Data storage

### Architecture

The data storage architecture is optimized to efficiently manage both real-time and historical data, leveraging Apache Druid for the ingestion and querying of time-series machine performance data. PostgreSQL is used to maintain structured data such as user information, alerts, and reports tables, ensuring reliable relational data storage. Additionally, Apache Ozone is employed as the object storage solution for managing and archiving reports. 
This architecture ensures scalability, high availability, and optimal performance for data-intensive operations, seamlessly integrating diverse storage and query needs.

### Prerequisites
+ [Docker](https://www.docker.com/get-started/) 
+ [PostgreSQL](https://www.postgresql.org/download/)

Required python modules:
+ [pandas](https://pandas.pydata.org/)
+ [psycopg2](https://pypi.org/project/psycopg2/)
+ [dotenv](https://pypi.org/project/python-dotenv/)

### Installation

To clone the repo:
```
git clone -b database https://github.com/belgio99/smartfactory
cd smartfactory
```
Create a folder named `obj_storage` and place the dataset there. Apache Druid can ingest denormalized data in JSON, CSV, TSV, or any custom delimited format. 
Support for PKL files has also been added.

Once the dataset is prepared, run the following python script:

```
python3 setup.py 
```
This will create a new datasource named `timeseries`, and will load the dataset into Druid.

To create the database tables for historical data, run the following python script:

```
python3 db_tables.py 
```

_Note:_ If you modified the ports in the Docker Compose file, ensure that the ports in the `.env` files are updated accordingly.

### Usage

Apache Druid supports two query languages: [Druid SQL](https://druid.apache.org/docs/latest/querying/sql) and [native queries](https://druid.apache.org/docs/latest/querying/) (JSON objects).

PosgreSQL supports [SQL queries](https://www.postgresql.org/docs/current/queries.html). You can see some query examples in the `db_tables.py` file.

### To-Do List
+ Swap the obj_storage folder with [Apache Ozone](https://ozone.apache.org/)
+ Implement encryption for sensitive data at rest.


