import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path) # Load environment variables from the .env file

def get_postgres_cursor():
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
    conn, cur = get_postgres_cursor()
    if cur:
        print("Cursor obtained successfully")
        # Don't forget to close the connection and cursor when done
        create_table_queries = [
            """
            CREATE TABLE IF NOT EXISTS Users (
            UserID SERIAL PRIMARY KEY,
            Username VARCHAR(50) NOT NULL,
            Email VARCHAR(50) NOT NULL,
            Role VARCHAR(20) NOT NULL,
            Password VARCHAR(255) NOT NULL,
            SiteName VARCHAR(50) NOT NULL,
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

        cur.close()
        conn.close()
