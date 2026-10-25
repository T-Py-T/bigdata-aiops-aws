import json
import logging
import os
from kafka import KafkaConsumer


def create_consumer():
    broker = os.environ.get("KAFKA_BROKER", "{{ KAFKA_BROKER }}")
    return KafkaConsumer(
        "ingest_topic",
        bootstrap_servers=[broker],
        value_deserializer=lambda message: json.loads(message.decode("utf-8")),
    )

def process_message(message):
    logging.info("Processing message: %s", message)

if __name__ == "__main__":
    for message in create_consumer():
        process_message(message.value)
