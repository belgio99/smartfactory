import os
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path) # Load environment variables from the .env file

def initialize_minio_client():
    """
    Initializes and returns a Minio client using environment variables.
    """

    return Minio(
        os.getenv('MINIO_HOST') + os.getenv('MINIO_ADDRESS'),  # Replace with your Minio server address
        access_key=os.getenv('MINIO_ROOT_USER'),  # Replace with your access key
        secret_key=os.getenv('MINIO_ROOT_PASSWORD'),  # Replace with your secret key
        secure=False  # Set to False if not using HTTPS
    )

def main():
    # Initialize the Minio client
    client = initialize_minio_client()

    # Define the bucket names
    reports_bucket_name = "reports"
    models_bucket_name = "models"

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
    except S3Error as exc:
        print("Error occurred while checking/creating buckets.", exc)

    # Uncomment and specify bucket name and file path to upload a file
    # bucket_name = "example-bucket"
    # file_path = "path/to/your/file.txt"
    # try:
    #     client.fput_object(bucket_name, file_path, file_path)
    #     print(f"'{file_path}' is successfully uploaded as object '{file_path}' to bucket '{bucket_name}'.")
    # except S3Error as exc:
    #     print("Error occurred while uploading file.", exc)

# Entry point
if __name__ == "__main__":
    main()
