from minio import Minio
import os
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_minio_client():
    return Minio(
        os.getenv('MINIO_HOST') + os.getenv('MINIO_ADDRESS'),
        access_key=os.getenv('MINIO_ROOT_USER'),
        secret_key=os.getenv('MINIO_ROOT_PASSWORD'),
        secure=False
    )