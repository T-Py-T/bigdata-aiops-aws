import json
import logging
from kafka import KafkaConsumer


def decode_kafka_value(raw_message: bytes):
    return json.loads(raw_message.decode("utf-8"))


def create_consumer():
    return KafkaConsumer(
        "ingest_topic",
        bootstrap_servers=["{{ KAFKA_BROKER }}"],
        value_deserializer=decode_kafka_value,
    )

def process_message(message):
    logging.info("Processing message: %s", message)

if __name__ == "__main__":
    for message in create_consumer():
        process_message(message.value)
