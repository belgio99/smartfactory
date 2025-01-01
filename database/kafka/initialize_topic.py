import subprocess
import os
from dotenv import load_dotenv
from pathlib import Path
from confluent_kafka.admin import AdminClient, NewTopic

# Load environment variables from the .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def create_kafka_topic(topic_name, bootstrap_server):
    """
    Creates a Kafka topic using the Kafka Admin API.

    Args:
        topic_name (str): Name of the Kafka topic to create.
        bootstrap_server (str): Kafka bootstrap server address.

    Raises:
        SystemExit: If the topic creation fails.
    """
    admin_client = AdminClient({"bootstrap.servers": bootstrap_server})
    
    topic_list = [NewTopic(topic_name, num_partitions=1, replication_factor=1)]
    future = admin_client.create_topics(topic_list)

    for topic, f in future.items():
        try:
            f.result()  # Wait for the topic to be created
            print(f"Topic {topic} created successfully.")
        except Exception as e:
            if "TopicExistsError" in str(e):
                print(f"Topic {topic} already exists. Skipping creation.")
            else:
                print(f"Failed to create topic {topic}: {e}")
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
    kafka_topic = os.getenv("TOPIC")
    kafka_bootstrap_server = os.getenv("KAFKA_SERVER")

    # Create Kafka topic
    create_kafka_topic(kafka_topic, kafka_bootstrap_server)

# Entry point
if __name__ == "__main__":
    main()
