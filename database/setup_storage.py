import subprocess
import os

## \file
#  \brief A script to sequentially execute multiple Python scripts and handle errors.

def run_script(script_path, description):
    """
    Executes a Python script located at `script_path` and handles errors.

    Args:
        script_path (str): Path to the Python script to execute.
        description (str): Description of the task being executed.

    Raises:
        SystemExit: If the script execution fails.
    """
    try:
        print(f"Starting: {description}")
        result = subprocess.run([
            "python3", script_path
        ], check=True, capture_output=True, text=True)
        print(f"Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        if "Topic already exists" in e.stderr or "already exists" in e.stdout:
            print(f"Info during {description}: Topic already exists.")
        else:
            print(f"Error during {description}\n{e.stderr}")
            exit(1)

def main():
    """
    Main function to define paths for scripts and execute them sequentially.

    Steps:
        1. Define paths for the Minio, PostgreSQL, and Druid scripts.
        2. Execute each script using the `run_script` function.

    Raises:
        SystemExit: If any of the scripts fail to execute.
    """
    # Define the paths to the scripts
    minio_script = os.path.join("minio", "create_obj_storage.py")
    postgres_script = os.path.join("postgres", "create_db_tables.py")
    druid_script = os.path.join("druid", "upload_timeseries.py")
    kafka_script = os.path.join("kafka", "initialize_topic.py")

    # Execute each script
    run_script(minio_script, "Creating Object Storage in Minio")
    run_script(postgres_script, "Creating Database Tables in PostgreSQL")
    run_script(druid_script, "Uploading Timeseries Data to Druid")
    run_script(kafka_script, "Creating a topic for Kafka")

# Entry point
if __name__ == "__main__":
    main()
