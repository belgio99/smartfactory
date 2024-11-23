import os
import psycopg2

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database using credentials from environment variables.
    Returns:
        tuple: A tuple containing the database connection and cursor objects.
               If the connection fails, returns (None, None).
    Raises:
        Exception: If there is an error connecting to the PostgreSQL database, it prints the error message.
    """
    try:
        connection = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT')
        )
        
        cursor = connection.cursor()
        
        return connection, cursor
    except Exception as error:
        print(f"Error connecting to PostgreSQL database: {error}")
        return None, None

def query_db(cursor, connection, query: str):
    """
    Executes a given SQL query using the provided cursor and connection.

    Args:
        cursor: The database cursor object used to execute the query.
        connection: The database connection object used to commit the transaction.
        query (str): The SQL query to be executed.

    Returns:
        The response from the cursor's execute method if the query is successful, otherwise None.

    Raises:
        Exception: If an error occurs during the execution of the query, it prints an error message and returns None.
    """
    try:
        response = cursor.execute(query)
        connection.commit()

        return response
    except Exception as error:
        print(f"Error querying PostgreSQL database: {error}")
        return None
