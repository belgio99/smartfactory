import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

## \file
#  \brief A script to manage PostgreSQL database connections and table creation for various microservices.

# Load environment variables from the .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_postgres_cursor():
    """
    Establishes a connection to the PostgreSQL database and returns the connection and cursor objects.

    Globals:
        POSTGRES_DB (str): The name of the PostgreSQL database.
        POSTGRES_USER (str): The username for the PostgreSQL database.
        POSTGRES_PASSWORD (str): The password for the PostgreSQL database.
        POSTGRES_HOST (str): The host address of the PostgreSQL database.
        POSTGRES_PORT (int): The port of the PostgreSQL database.

    Raises:
        Exception: If there is an error connecting to the PostgreSQL database.

    Returns:
        tuple: A tuple containing the connection and cursor objects. Returns (None, None) on failure.
    """
    try:
        # Connect to your postgres DB
        connection = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT')
        )

        # Create a cursor object
        cursor = connection.cursor()

        return connection, cursor
    except Exception as error:
        print(f"Error connecting to PostgreSQL database: {error}")
        return None, None

if __name__ == "__main__":
    """
    Main entry point of the script. Manages table creation and data operations.

    Globals:
        POSTGRES_DB (str): The name of the PostgreSQL database.
        POSTGRES_USER (str): The username for the PostgreSQL database.
        POSTGRES_PASSWORD (str): The password for the PostgreSQL database.
        POSTGRES_HOST (str): The host address of the PostgreSQL database.
        POSTGRES_PORT (int): The port of the PostgreSQL database.

    """
    conn, cur = get_postgres_cursor()
    if cur:
        print("Cursor obtained successfully")

        # Queries for creating tables
        create_table_queries = [
            """
            CREATE TABLE IF NOT EXISTS Users (
            UserID SERIAL PRIMARY KEY,
            Username VARCHAR(300) NOT NULL,
            Email VARCHAR(300) NOT NULL,
            Role VARCHAR(300) NOT NULL,
            Password VARCHAR(255) NOT NULL,
            SiteName VARCHAR(300) NOT NULL,
            UserSettings TEXT,
            UserDashboards TEXT,
            UserSchedules TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Reports (
            ReportID SERIAL PRIMARY KEY,
            Name VARCHAR(100) NOT NULL,
            Type VARCHAR(100) NOT NULL,
            OwnerID INT NOT NULL,
            GeneratedAt TIMESTAMP NOT NULL,
            FilePath TEXT NOT NULL,
            SiteName VARCHAR(50) NOT NULL,
            FOREIGN KEY (OwnerID) REFERENCES Users(UserID)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Alerts (
            AlertID SERIAL PRIMARY KEY,
            Title VARCHAR(50) NOT NULL,
            Type VARCHAR(50) NOT NULL,
            Description VARCHAR(255) NOT NULL,
            TriggeredAt TIMESTAMP NOT NULL,
            MachineName VARCHAR(50) NOT NULL,
            isPush BOOLEAN DEFAULT FALSE,
            Severity VARCHAR(10) NOT NULL
            CHECK (Severity IN ('Low', 'Medium', 'High'))
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS AlertRecipients (
            ID SERIAL PRIMARY KEY,
            AlertID INT NOT NULL,
            UserID INT NOT NULL,
            Read BOOLEAN NOT NULL DEFAULT FALSE,
            UNIQUE(AlertID, UserID),
            FOREIGN KEY (AlertID) REFERENCES Alerts(AlertID) ON DELETE CASCADE,
            FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Models (
            ID SERIAL PRIMARY KEY,
            KPI VARCHAR(50) NOT NULL,
            MachineName VARCHAR(50) NOT NULL,
            ModelPath TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Microservices (
            ServiceID VARCHAR(20) PRIMARY KEY,
            Key VARCHAR(50) NOT NULL
            )
            """
        ]

        # Execute table creation queries
        for query in create_table_queries:
            cur.execute(query)
            conn.commit()

        print("Tables created successfully")

        # Insert dummy data into the Microservices table

        demo_api_keys_query = """
        INSERT INTO Microservices (ServiceID, Key) VALUES
        ('api-layer', '06e9b31c-e8d4-4a6a-afe5-fc7b0cc045a7'),
        ('ai-agent', 'a3ebe1bb-a4e7-41a3-bbcc-6c281136e234'),
        ('kpi-engine', 'b3ebe1bb-a4e7-41a3-bbcc-6c281136e234'),
        ('knowledge-base', 'c3ebe1bb-a4e7-41a3-bbcc-6c281136e234'),
        ('data', '12d326d6-8895-49b9-8e1b-a760462ac13f'),
        ('gui', '111c50cc-6b03-4c01-9d2f-aac6b661b716')
        ON CONFLICT (ServiceID) DO NOTHING;
        """
        cur.execute(demo_api_keys_query)
        conn.commit()
        print("Demo API Keys inserted into Microservices table")

        # Close cursor and connection
        cur.close()
        conn.close()
