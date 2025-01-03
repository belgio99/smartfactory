import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def submit_supervisor_spec(druid_host, kafka_topic, druid_datasource):
    """
    Submits a Druid Kafka supervisor spec to ingest data from Kafka.

    Args:
        druid_host (str): Host URL of the Druid Overlord (e.g., http://localhost:8081).
        kafka_topic (str): Name of the Kafka topic to consume data from.
        druid_datasource (str): Name of the Druid datasource.

    Raises:
        SystemExit: If the submission fails.
    """
    supervisor_spec = {
        "type": "kafka",
        "dataSchema": {
            "dataSource": druid_datasource,
            "timestampSpec": {
                "column": "time",
                "format": "iso"
            },
            "dimensionsSpec": {
                "dimensions": ["asset_id", "name", "kpi"]
            },
            "metricsSpec": [
                {"type": "doubleSum", "name": "sum", "fieldName": "sum"},
                {"type": "doubleSum", "name": "avg", "fieldName": "avg"},
                {"type": "doubleMin", "name": "min", "fieldName": "min"},
                {"type": "doubleMax", "name": "max", "fieldName": "max"}
                ]
        },
        "ioConfig": {
            "topic": kafka_topic,
            "consumerProperties": {
                "bootstrap.servers": os.getenv('KAFKA_SERVER')
            },
            "useEarliestOffset": True,
            "inputFormat": {  # Define the input format for the data
                "type": "json",
                "flattenSpec": {
                    "useFieldDiscovery": True
                }
            }
        },
        "tuningConfig": {
            "type": "kafka",
            "maxRowsInMemory": 100000,
            "intermediatePersistPeriod": "PT10M",
            "maxRowsPerSegment": 5000000
        }
    }

    try:
        url = f"{druid_host}/druid/indexer/v1/supervisor"
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, headers=headers, data=json.dumps(supervisor_spec))
        
        if response.status_code == 200:
            print(f"Successfully submitted supervisor spec for datasource '{druid_datasource}'.")
        else:
            print(f"Failed to submit supervisor spec: {response.status_code} - {response.text}")
            exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Druid Overlord: {e}")
        exit(1)

def main():
    """
    Main function to configure and submit the Druid Kafka supervisor spec.
    """
    # Druid Overlord URL
    druid_host = os.getenv("DRUID_COORDINATOR_ENDPOINT")
    
    # Kafka topic and Druid datasource
    kafka_topic = os.getenv("TOPIC", "machine_logs")
    druid_datasource = os.getenv("DRUID_DATASOURCE")
    
    print(f"Submitting supervisor spec for topic '{kafka_topic}' to datasource '{druid_datasource}'.")
    submit_supervisor_spec(druid_host, kafka_topic, druid_datasource)

if __name__ == "__main__":
    main()
