This is the branch dedicated to the development of the API Layer. It's currently integrated with the database branch, in order to have a shared environment for setting up the data storage. 

To run the service, just run "docker compose up" in the main directory. 
This will start all the services and the endpoints will be active to handle requests.

To populate the database, execute the python script "db_tables.py".
Once done that, the database will contain some mock data for testing purposes. 
