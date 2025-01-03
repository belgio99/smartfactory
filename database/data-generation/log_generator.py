import random
import time
from datetime import datetime
from kafka import KafkaProducer
import json
import os

from dotenv import load_dotenv

load_dotenv()

# Mapping of machines to unique asset IDs
machine_to_asset_id = {
    'Large Capacity Cutting Machine 1': 'ast-yhccl1zjue2t',
    'Large Capacity Cutting Machine 2': 'ast-6votor3o4i9l',
    'Medium Capacity Cutting Machine 1': 'ast-ha448od5d6bd',
    'Medium Capacity Cutting Machine 2': 'ast-5aggxyk5hb36',
    'Medium Capacity Cutting Machine 3': 'ast-anxkweo01vv2',
    'Low Capacity Cutting Machine 1': 'ast-6nv7viesiao7',
    'Laser Welding Machine 1': 'ast-hnsa8phk2nay',
    'Laser Welding Machine 2': 'ast-206phi0b9v6p',
    'Assembly Machine 1': 'ast-pwpbba0ewprp',
    'Assembly Machine 2': 'ast-upqd50xg79ir',
    'Assembly Machine 3': 'ast-sfio4727eub0',
    'Testing Machine 1': 'ast-nrd4vl07sffd',
    'Testing Machine 2': 'ast-pu7dfrxjf2ms',
    'Testing Machine 3': 'ast-06kbod797nnp',
    'Riveting Machine': 'ast-o8xtn5xa8y87',
    'Laser Cutter': 'ast-xpimckaf3dlf'
}

# List of KPIs
kpis = [
    'working_time', 'idle_time', 'offline_time',
    'consumption', 'power', 'cost', 'consumption_working', 'consumption_idle',
    'cycles', 'good_cycles', 'bad_cycles', 'average_cycle_time'
]

# Generate random KPI values
def generate_kpi_values():
    return {
        'sum': round(random.uniform(0, 1000), 2),
        'avg': round(random.uniform(0, 100), 2),
        'min': round(random.uniform(0, 50), 2),
        'max': round(random.uniform(50, 100), 2)
    }

# Function to generate logs
def generate_logs(interval_seconds, kafka_topic, kafka_server):

    producer = KafkaProducer(
        bootstrap_servers=kafka_server,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print(f"Generating logs every {interval_seconds} seconds. Sending to Kafka topic '{kafka_topic}' using server '{kafka_server}'. Press Ctrl+C to stop.")

    while True:
        current_time = datetime.now()
        for machine, asset_id in machine_to_asset_id.items():
            for kpi in kpis:
                kpi_values = generate_kpi_values()
                log_entry = {
                    "time": current_time.isoformat(),
                    "asset_id": asset_id,
                    "name": machine,
                    "kpi": kpi,
                    "sum": kpi_values['sum'],
                    "avg": kpi_values['avg'],
                    "min": kpi_values['min'],
                    "max": kpi_values['max']
                }
                print(log_entry)
                producer.send(kafka_topic, log_entry)

        time.sleep(interval_seconds)

# Main script entry point
if __name__ == "__main__":
    try:
        kafka_server = os.getenv('KAFKA_SERVER', 'localhost:9092')
        kafka_topic = os.getenv('TOPIC', 'machine_logs')
        interval_seconds = int(os.getenv('INTERVAL', 5))

        generate_logs(interval_seconds, kafka_topic, kafka_server)
    except KeyboardInterrupt:
        print("Log generation stopped.")
