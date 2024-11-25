from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from the .env file

# Initialize the Minio client
client = Minio(
    os.getenv('MINIO_HOST') + os.getenv('MINIO_ADDRESS'),  # Replace with your Minio server address
    access_key=os.getenv('MINIO_ROOT_USER'),  # Replace with your access key
    secret_key=os.getenv('MINIO_ROOT_PASSWORD'),  # Replace with your secret key
    secure=False  # Set to False if not using HTTPS
)

# Define the bucket name and file path
bucket_name = "my-bucket"
file_path = "test.json"

# Create the bucket if it doesn't exist
if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)

# Upload the file
try:
    client.fput_object(bucket_name, file_path, file_path)
    print(f"'{file_path}' is successfully uploaded as object '{file_path}' to bucket '{bucket_name}'.")
except S3Error as exc:
    print("Error occurred.", exc)