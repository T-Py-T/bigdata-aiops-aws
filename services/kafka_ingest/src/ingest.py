import json
import logging
import os
from kafka import KafkaProducer
from fastapi import FastAPI

app = FastAPI()


def create_producer():
    broker = os.environ.get("KAFKA_BROKER", "{{ KAFKA_BROKER }}")
    return KafkaProducer(
        bootstrap_servers=[broker],
        value_serializer=lambda value: json.dumps(value).encode(),
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ingest")
def ingest_data(payload: dict):
    producer = create_producer()
    try:
        producer.send("ingest_topic", payload)
        producer.flush()
        logging.info("Data ingested: %s", payload)
    finally:
        producer.close()
    return {"message": "Data ingested"}
