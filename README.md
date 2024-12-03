## Data storage

### Architecture

![architecture](https://github.com/user-attachments/assets/3db6089f-f630-4f27-bb1e-e87b9cafb477)

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
