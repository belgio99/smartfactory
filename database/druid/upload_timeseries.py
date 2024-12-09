import os
import sys
import pandas as pd
import requests
from dotenv import load_dotenv
from pathlib import Path

## \file
#  \brief A script for managing file conversion to CSV and submitting ingestion tasks to Apache Druid.

# Load environment variables from the .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Add the parent directory of 'vault' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vault.crypto_lib import encrypt_csv

def convert_to_csv(file_path):
    """
    Converts a given file to CSV format if necessary.

    Args:
        file_path (str): The path of the file to be converted.

    Raises:
        ValueError: If the file format is unsupported.

    Returns:
        str: The path of the converted CSV file.
    """
    file_name, file_extension = os.path.splitext(file_path)
    csv_path = file_name + '.csv'

    if file_extension == '.pkl':
        df = pd.read_pickle(file_path)
        df.to_csv(csv_path, index=False)
        return csv_path
    elif file_extension == '.csv':
        return file_path  # Already a CSV, no conversion needed
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

def submit_to_druid(file_path):
    """
    Prepares and submits the ingestion task to Apache Druid for the given CSV file.

    Args:
        file_path (str): The path of the CSV file to be submitted.

    Globals:
        DRUID_INSERT_ENDPOINT (str): The Druid ingestion endpoint.
        TO_LOAD_DIR (str): The directory containing the files to be loaded.

    Raises:
        Exception: If the submission to Druid fails.
    """
    ingestion_spec = {
        "type": "index",
        "spec": {
            "dataSchema": {
                "dataSource": "timeseries",
                "timestampSpec": {
                    "column": "time",
                    "format": "auto"
                },
                "dimensionsSpec": {
                    "dimensions": [
                        {"name": "asset_id", "type": "string"},
                        {"name": "name", "type": "string"},
                        {"name": "kpi", "type": "string"},
                        {"name": "avg", "type": "double", "fieldName": "avg"},
                        {"name": "sum", "type": "double", "fieldName": "sum"},
                        {"name": "min", "type": "double", "fieldName": "min"},
                        {"name": "max", "type": "double", "fieldName": "max"}
                    ]
                },
                "granularitySpec": {
                    "type": "uniform",
                    "segmentGranularity": "MONTH",
                    "queryGranularity": "NONE",
                    "rollup": False
                },
            },
            "ioConfig": {
                "type": "index",
                "inputSource": {
                    "type": "local",
                    "baseDir": "/" + os.getenv('TO_LOAD_DIR'),
                    "filter": os.path.basename(file_path)
                },
                "inputFormat": {
                    "type": "csv",
                    "findColumnsFromHeader": True
                }
            },
            "tuningConfig": {
                "type": "index"
            }
        }
    }

    response = requests.post(os.getenv('DRUID_INSERT_ENDPOINT'), json=ingestion_spec)

    if response.status_code == 200:
        print(f"Task submitted successfully for file: {file_path}")
    else:
        print(f"Failed to submit task for file: {file_path}, response: {response.text}")

def main():
    """
    Main function to first convert files to CSV if necessary,
    and then submit only the CSV files to Apache Druid.

    Globals:
        TO_LOAD_DIR (str): The directory containing files to be processed.
    """
    csv_files = []

    TO_LOAD_DIR = os.getenv("TO_LOAD_DIR")

    # First convert files to CSV if necessary
    for file_name in os.listdir(TO_LOAD_DIR):
        file_path = os.path.join(TO_LOAD_DIR, file_name)

        if os.path.isfile(file_path) and not file_name.endswith('.csv'):
            try:
                # Convert the file to CSV if necessary
                csv_file_path = convert_to_csv(file_path)

                # Overwrite any existing file in the dictionary with the same name
                csv_files.append(csv_file_path)

            except ValueError as e:
                print(f"Skipping file {file_name}: {e}")
            except Exception as e:
                print(f"An error occurred during conversion of {file_name}: {e}")

    # Check if the list of CSV files is empty
    if not csv_files:
        print("Upload folder empty")

    # Then submit only the CSV files to Druid
    for csv_file_path in csv_files:
        if not csv_file_path.endswith('.csv'):
            continue
        try:
            # The following functions encrypt the csv file before submitting it to druid.
            # Remove comments if you want to encrypt files.
            # encrypt file
            # df = encrypt_csv(csv_file_path)

            # Save the encrypted file
            # encrypted_file_path = csv_file_path.replace(".csv", "_encrypted.csv")
            # df.to_csv(encrypted_file_path, index=False)
            # print(f"Encrypted file saved at: {encrypted_file_path}")
            # submit_to_druid(encrypted_file_path)

            submit_to_druid(csv_file_path)
        except Exception as e:
            print(f"An error occurred during submission of {csv_file_path}: {e}")

if __name__ == "__main__":
    main()
