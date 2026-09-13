import json
import logging
from kafka import KafkaConsumer


def create_consumer():
    return KafkaConsumer(
        "ingest_topic",
        bootstrap_servers=["{{ KAFKA_BROKER }}"],
        value_deserializer=lambda message: json.loads(message.decode("utf-8")),
    )

def process_message(message):
    logging.info("Processing message: %s", message)

if __name__ == "__main__":
    for message in create_consumer():
        process_message(message.value)
