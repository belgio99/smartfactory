
## Data storage

### Prerequisites

+ [Docker](https://www.docker.com/get-started/) 
+ [pandas](https://pandas.pydata.org/)

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
This will create a new datasource named `timeseries`, and will load the dataset into Druid
_Note:_ If you modified the ports in the Docker Compose file, ensure that the ports in the script are updated accordingly.

### Usage

Apache Druid supports two query languages: [Druid SQL](https://druid.apache.org/docs/latest/querying/sql) and [native queries](https://druid.apache.org/docs/latest/querying/) (JSON objects).

Currently, only time series data can be queried.

### To-Do List
+ Add support for historical data (user, reports, alarms, forecast)
+ Swap the obj_storage folder with [Apache Ozone](https://ozone.apache.org/)
+ Add the [Basic Security](https://druid.apache.org/docs/latest/development/extensions-core/druid-basic-security/) Druid extension.
+ Implement encryption for sensitive data at rest.


