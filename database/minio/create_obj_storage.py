import os
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
from pathlib import Path

## \file
#  \brief A script to initialize a Minio client and manage bucket operations.

# Load environment variables from the .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def initialize_minio_client():
    """
    Initializes and returns a Minio client using environment variables.

    Globals:
        MINIO_HOST (str): The Minio server host.
        MINIO_ADDRESS (str): The Minio server address.
        MINIO_ROOT_USER (str): The root user for Minio.
        MINIO_ROOT_PASSWORD (str): The root password for Minio.

    Returns:
        Minio: An instance of the Minio client.
    """
    return Minio(
        os.getenv('MINIO_HOST') + os.getenv('MINIO_ADDRESS'),
        access_key=os.getenv('MINIO_ROOT_USER'),
        secret_key=os.getenv('MINIO_ROOT_PASSWORD'),
        secure=False
    )

def main():
    """
    Main function to initialize the Minio client, and create buckets if they do not exist.

    Globals:
        MINIO_HOST (str): The Minio server host.
        MINIO_ADDRESS (str): The Minio server address.
        MINIO_ROOT_USER (str): The root user for Minio.
        MINIO_ROOT_PASSWORD (str): The root password for Minio.
    """
    # Initialize the Minio client
    client = initialize_minio_client()

    # Define the bucket names
    reports_bucket_name = "reports"
    models_bucket_name = "models"
    dashboards_bucket_name = "dashboards"
    schedules_bucket_name = "schedules"

    # Create the buckets if they don't exist
    try:
        if not client.bucket_exists(reports_bucket_name):
            client.make_bucket(reports_bucket_name)
            print(f"Bucket '{reports_bucket_name}' created successfully.")
        else:
            print(f"Bucket '{reports_bucket_name}' already exists.")

        if not client.bucket_exists(models_bucket_name):
            client.make_bucket(models_bucket_name)
            print(f"Bucket '{models_bucket_name}' created successfully.")
        else:
            print(f"Bucket '{models_bucket_name}' already exists.")

        if not client.bucket_exists(dashboards_bucket_name):
            client.make_bucket(dashboards_bucket_name)
            print(f"Bucket '{dashboards_bucket_name}' created successfully.")
        else:
            print(f"Bucket '{dashboards_bucket_name}' already exists.")

        if not client.bucket_exists(schedules_bucket_name):
            client.make_bucket(schedules_bucket_name)
            print(f"Bucket '{schedules_bucket_name}' created successfully.")
        else:
            print(f"Bucket '{schedules_bucket_name}' already exists.")
    except S3Error as exc:
        print("Error occurred while checking/creating buckets.", exc)


# Entry point
if __name__ == "__main__":
    main()
