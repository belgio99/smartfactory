import subprocess
import os

def run_script(script_path, description):
    """
    Executes a Python script located at `script_path` and handles errors.
    :param script_path: Path to the Python script to execute.
    :param description: Description of the task being executed.
    """
    try:
        print(f"Starting: {description}")
        result = subprocess.run(["python3", script_path], check=True, capture_output=True, text=True)
        print(f"Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error during: {description}\n{e.stderr}")
        exit(1)

def main():
    # Define the paths to the scripts
    minio_script = os.path.join("minio", "create_obj_storage.py")
    postgres_script = os.path.join("postgres", "create_db_tables.py")
    druid_script = os.path.join("druid", "upload_timeseries.py")

    # Execute each script
    run_script(minio_script, "Creating Object Storage in Minio")
    run_script(postgres_script, "Creating Database Tables in PostgreSQL")
    run_script(druid_script, "Uploading Timeseries Data to Druid")

if __name__ == "__main__":
    main()
