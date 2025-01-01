import subprocess
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def create_kafka_topic(topic_name, bootstrap_server):
    """
    Creates a Kafka topic using `kafka-topics.sh`.

    Args:
        topic_name (str): Name of the Kafka topic to create.
        bootstrap_server (str): Kafka bootstrap server address.

    Raises:
        SystemExit: If the topic creation fails.
    """
    try:
        print(f"Creating Kafka topic: {topic_name}")
        result = subprocess.run([
            "/opt/bitnami/kafka/bin/kafka-topics.sh",
            "--create",
            "--topic", topic_name,
            "--bootstrap-server", bootstrap_server,
            "--partitions", "1",
            "--replication-factor", "1"
        ], check=True, capture_output=True, text=True)
        print(f"Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        if "Topic already exists" in e.stderr:
            print(f"Topic {topic_name} already exists. Skipping creation.")
        else:
            print(f"Error creating Kafka topic: {topic_name}\n{e.stderr}")
            exit(1)

def main():
    """
    Main function to initialize Kafka topics.

    Steps:
        1. Fetch Kafka topic and bootstrap server from environment variables.
        2. Create Kafka topic.

    Raises:
        SystemExit: If any of the steps fail.
    """
    # Kafka configuration
    kafka_topic = os.getenv("KAFKA_TOPIC", "machine_logs")
    kafka_bootstrap_server = os.getenv("KAFKA_SERVER", "localhost:9092")

    # Create Kafka topic
    create_kafka_topic(kafka_topic, kafka_bootstrap_server)

# Entry point
if __name__ == "__main__":
    main()
