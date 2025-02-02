from .minio_client import get_minio_client
from .postgres_client import get_postgres_connection
import io
import json

def delete_duplicate_models(bucket_name):
    client = get_minio_client()
    # Ensure the bucket exists
    if client.bucket_exists(bucket_name):
    
        # Insert or update record into PostgreSQL
        try:
            conn = get_postgres_connection()
            cursor = conn.cursor()
            select_query = """
            Select * FROM Models
            WHERE ctid NOT IN (
            SELECT MIN(ctid)
            FROM Models
            GROUP BY KPI, MachineName, ModelPath
            );
            """
            cursor.execute(select_query)
            existing_records = cursor.fetchall()
            print("candidate records: ", existing_records)
            if(len(existing_records) > 0):

                delete_query = """
                DELETE FROM Models
                WHERE ctid NOT IN (
                    SELECT MIN(ctid)
                    FROM Models
                    GROUP BY KPI, MachineName, ModelPath
                );
                """
                cursor.execute(delete_query)
                conn.commit()
                print("entry deleted from DB")

                for record in existing_records:
                    file_name = record[3][7:]
                    client.remove_object(bucket_name, file_name)
                    print(f"File '{file_name}' removed from bucket '{bucket_name}'.")
            else:
                print("no duplicates found")


        except Exception as e:
            print("Error inserting into PostgreSQL:", e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    else:
        print(f"Bucket '{bucket_name}' not found.")
    pass

# Insert a JSON model into the bucket
def insert_model_to_storage(bucket_name, file_name, json_data, kpi, machine_name):
    client = get_minio_client()
    # Ensure the bucket exists
    if client.bucket_exists(bucket_name):
        # Convert JSON data to bytes
        json_bytes = json.dumps(json_data).encode('utf-8')
        
        # Upload JSON data
        client.put_object(
            bucket_name,
            file_name,
            data=io.BytesIO(json_bytes),
            length=len(json_bytes),
            content_type="application/json"
        )
        print(f"File '{file_name}' uploaded to bucket '{bucket_name}'.")

        # Insert or update record into PostgreSQL
        try:
            conn = get_postgres_connection()
            cursor = conn.cursor()
            model_path = f"{bucket_name}/{file_name}"

            # Check if record already exists in PostgreSQL
            select_query = """
            SELECT ID FROM Models
            WHERE KPI = %s AND MachineName = %s;
            """
            cursor.execute(select_query, (kpi, machine_name))
            existing_record = cursor.fetchone()

            if existing_record:
                # Update the existing record
                update_query = """
                UPDATE Models
                SET ModelPath = %s
                WHERE KPI = %s AND MachineName = %s;
                """
                cursor.execute(update_query, (model_path, kpi, machine_name))
                conn.commit()
                print(f"Record for KPI '{kpi}' and Machine '{machine_name}' updated in PostgreSQL.")
            else:
                # Insert a new record
                insert_query = """
                INSERT INTO Models (KPI, MachineName, ModelPath)
                VALUES (%s, %s, %s)
                RETURNING ID;
                """
                cursor.execute(insert_query, (kpi, machine_name, model_path))
                record_id = cursor.fetchone()[0]
                conn.commit()
                print(f"Record inserted into PostgreSQL with ID: {record_id}")


        except Exception as e:
            print("Error inserting into PostgreSQL:", e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    else:
        print(f"Bucket '{bucket_name}' not found.")
    pass

# Retrieve a JSON model from the bucket
def retrieve_model_from_storage(kpi, machine_name):
    try:
        # Query PostgreSQL for the file path
        conn = get_postgres_connection()
        cursor = conn.cursor()
        select_query = """
        SELECT ModelPath FROM Models
        WHERE KPI = %s AND MachineName = %s;
        """
        cursor.execute(select_query, (kpi, machine_name))
        result = cursor.fetchone()
        if result is None:
            print(f"No record found for KPI: {kpi} and MachineName: {machine_name}")
            return None
        model_path = result[0]
        bucket_name, file_name = model_path.split('/', 1)

        # Retrieve JSON object from MinIO
        client = get_minio_client()
        response = client.get_object(bucket_name, file_name)
        json_data = json.load(response)
        response.close()
        response.release_conn()
        print(f"JSON data retrieved for KPI: {kpi} and MachineName: {machine_name}")
        return json_data
    except Exception as e:
        print("Error occurred:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    pass

# Retrieve all JSON models from the storage
def retrieve_all_models_from_storage():
    try:
        # Query PostgreSQL for all file paths
        conn = get_postgres_connection()
        cursor = conn.cursor()
        select_query = """
        SELECT KPI, MachineName, ModelPath FROM Models;
        """
        cursor.execute(select_query)
        results = cursor.fetchall()

        all_models = []
        client = get_minio_client()

        for kpi, machine_name, model_path in results:
            bucket_name, file_name = model_path.split('/', 1)

            try:
                # Retrieve JSON object from MinIO
                response = client.get_object(bucket_name, file_name)
                json_data = json.load(response)
                response.close()
                response.release_conn()

                all_models.append({
                    "KPI": kpi,
                    "MachineName": machine_name,
                    "ModelPath": model_path,
                    "Data": json_data
                })
            except Exception as e:
                print(f"Error retrieving file {file_name} from bucket {bucket_name}: {e}")

        print("All models retrieved successfully.")
        return all_models
    except Exception as e:
        print("Error occurred while retrieving all models:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()