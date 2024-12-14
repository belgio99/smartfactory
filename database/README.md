
## Data storage

### Architecture

![architecture](https://github.com/user-attachments/assets/557bcb98-e7d7-4130-8801-3e2351bc5830)

The data storage architecture is optimized to efficiently manage both real-time and historical data, leveraging [Apache Druid](https://druid.apache.org/) for the ingestion and querying of time-series machine performance data. [PostgreSQL](https://www.postgresql.org/) is used to maintain structured data such as user information, alerts, and reports tables, ensuring reliable relational data storage. Additionally, [MinIO](https://min.io/) is employed as the object storage solution for managing and archiving reports. 
This architecture ensures scalability, high availability, and optimal performance for data-intensive operations, seamlessly integrating diverse storage and query needs.

### Prerequisites

+ [Docker](https://www.docker.com/get-started/) 

### Installation

To clone the repository:
```
git clone -b database https://github.com/belgio99/smartfactory
cd smartfactory
```
To start the containers:

```
docker compose up -d
```
The next steps for initializing the database are outlined in the `README` file within the `database` folder:

```
cd database
```


## Data storage

### Bundled Python Modules

The following Python modules are installed during the Docker image build process:
+ [pandas](https://pandas.pydata.org/): Data analysis and manipulation library.
+ [psycopg2-binary](https://pypi.org/project/psycopg2-binary/): PostgreSQL database adapter for Python.
+ [hvac](https://pypi.org/project/hvac/): Python client for HashiCorp Vault.
+ [minio](https://min.io/docs/minio/linux/developers/python/minio-py.html): Python library for interacting with Minio object storage.
+ [dotenv](https://pypi.org/project/python-dotenv/): Loads environment variables from a `.env` file.

### Initialization Steps

1. **Prepare the Dataset** 
		Create an `upload` folder inside the `druid` subdirectory:
	``` 
	mkdir -p druid/upload 
	``` 
	 Place then your dataset in the `druid/upload` folder. 
	 Apache Druid can ingest denormalized data in JSON, CSV, TSV, or any custom delimited format. Support for PKL files has also been added.
 
2. **Build the Docker Image** 
	Build the initialization image using the following command:
	``` 
	docker build -t smartfactory-db-init .
	``` 
	_Note:_ If you modified the ports in the Docker Compose file, ensure that the ports in the `.env` files are updated accordingly.
3. **Run the Image in a container**
	Execute the following command to set up the database architecture:
	``` 
	docker run --rm --network host --name init -v ./druid/upload:/app/druid/upload smartfactory-db-init
	``` 
	The container will automatically remove itself once the process is complete.
### What the Initialization Does

1.  **Creates Object Storage in Minio**:  
    Initializes the object storage in Minio to manage and archive reports, creating the necessary buckets for `reports` and `backups` if they do not already exist.
    
2.  **Creates Database Tables in PostgreSQL**:  
    Sets up the database tables in PostgreSQL for structured data (tables for user information, alerts, and reports).
    
3.  **Uploads Time-Series Data to Apache Druid**:  
    Ingests the dataset placed in the `obj_storage` folder into Apache Druid, creating a new datasource named `timeseries`.

	
