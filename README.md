# api branch

This is the branch dedicated to the development of the API Layer. It's currently integrated with the database branch, in order to have a shared environment for setting up the data storage.

## To run

-   To run the service, just run _docker compose up_ in the main directory. This will start all the services and the endpoints will be active to handle requests.

## To test endpoints

-   To populate the PostgreSQL database, execute the python script _db_tables.py_. Once done that, the database will contain some mock data for testing purposes.
-   To populate the Minio database, execute the python script _setup_minio.py_.
