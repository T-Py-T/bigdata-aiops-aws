import json
import logging
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "ingest_topic",
    bootstrap_servers=["{{ KAFKA_BROKER }}"],
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

def process_message(message):
    logging.info("Processing message: %s", message)

if __name__ == "__main__":
    for msg in consumer:
        process_message(msg.value)
