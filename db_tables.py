import os
from dotenv import load_dotenv
import psycopg2

load_dotenv() # Load environment variables from the .env file

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
            Password VARCHAR(250) NOT NULL,
            SiteName VARCHAR(50) NOT NULL,
            UserSettings TEXT,
            UserDashboards TEXT
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
            AlertID VARCHAR(36) PRIMARY KEY,
            Title VARCHAR(255) NOT NULL,
            Type VARCHAR(255) NOT NULL,
            Description VARCHAR(255) NOT NULL,
            TriggeredAt TIMESTAMP NOT NULL,
            MachineName VARCHAR(255) NOT NULL,
            isPush BIT NOT NULL,
            Recipients VARCHAR(255) NOT NULL,
            Severity VARCHAR(10) NOT NULL
            CHECK (Severity IN ('Low', 'Medium', 'High'))
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
            response = cur.execute(query)
            conn.commit()
            print(response)


        # Insert dummy data into the Microservices table

        dummy_microservices_keys_query = """
        INSERT INTO Microservices (ServiceID, Key) VALUES
        ('api-layer', '06e9b31c-e8d4-4a6a-afe5-fc7b0cc045a7'),
        ('ai-agent', 'a3ebe1bb-a4e7-41a3-bbcc-6c281136e234'),
        ('kpi-engine', 'b3ebe1bb-a4e7-41a3-bbcc-6c281136e234'),
        ('knowledge-base', 'c3ebe1bb-a4e7-41a3-bbcc-6c281136e234'),
        ('data', '12d326d6-8895-49b9-8e1b-a760462ac13f'),
        ('gui', '111c50cc-6b03-4c01-9d2f-aac6b661b716');
        """
        cur.execute(dummy_microservices_keys_query)
        conn.commit()
        print("Dummy data inserted into Microservices table")

        # insert_users_query = """
        # INSERT INTO Users (Username, Email, Role, Password, SiteName) VALUES
        # ('john_doe', 'john@example.com', 'admin', 'password123', 'SiteA'),
        # ('jane_smith', 'jane@example.com', 'user', 'password456', 'SiteB'),
        # ('alice_jones', 'alice@example.com', 'user', 'password789', 'SiteC')
        # """
        # cur.execute(insert_users_query)
        # conn.commit()
        # print("Dummy data inserted into Users table")

        get_users_query = """
        SELECT * FROM Users
        """
        cur.execute(get_users_query)
        conn.commit()
        print("Data retrieved from Users table")
        rows = cur.fetchall()
        for row in rows:
           print(row)

        
        cur.close()
        conn.close()