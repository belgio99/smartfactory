# TODO: fix imports
''' 
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from the .env file

def get_minio_connection():
    """
    Establishes a connection to the Minio object storage service using credentials from environment variables.
    Returns:
        Minio: A Minio client object.
    """
    return Minio(
        os.getenv('MINIO_HOST') + os.getenv('MINIO_ADDRESS'),  # Replace with your Minio server address
        access_key=os.getenv('MINIO_ROOT_USER'),  # Replace with your access key
        secret_key=os.getenv('MINIO_ROOT_PASSWORD'),  # Replace with your secret key
        secure=False  # Set to False if not using HTTPS
    )

def upload_object(client: Minio, bucket_name: str, object_name: str, file_path: str):
    """
    Uploads a file to the Minio object storage service.

    Args:
        client (Minio): The Minio client object used to interact with the object storage service.
        bucket_name (str): The name of the bucket where the file will be uploaded.
        file_path (str): The path to the file to be uploaded.

    Returns:
        bool: True if the file is successfully uploaded, otherwise False.
    """
    # Create the bucket if it doesn't exist
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print("Bucket not found, creating one.")
    # Upload the file
    try:
        client.fput_object(bucket_name, object_name, file_path)
        print(f"'{file_path}' is successfully uploaded as object '{object_name}' to bucket '{bucket_name}'.")
        return True
    except S3Error as exc:
        print("Error occurred.", exc)
        return False
    

def download_object(client: Minio, bucket_name: str, object_name: str, file_path: str):
    """
    Downloads a file from the Minio object storage service.

    Args:
        client (Minio): The Minio client object used to interact with the object storage service.
        bucket_name (str): The name of the bucket where the file is located.
        object_name (str): The name of the object to be downloaded.
        file_path (str): The path to the file to be downloaded.

    Returns:
        bool: True if the file is successfully downloaded, otherwise False.
    """
    try:
        client.fget_object(bucket_name, object_name, file_path)
        print(f"'{object_name}' is successfully downloaded from bucket '{bucket_name}' as object '{file_path}'.")
        return True
    except S3Error as exc:
        print("Error occurred.", exc)
        return False
'''