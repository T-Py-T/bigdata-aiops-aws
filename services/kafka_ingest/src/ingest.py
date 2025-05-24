import json
import logging
from kafka import KafkaProducer
from fastapi import FastAPI

app = FastAPI()
producer = KafkaProducer(
    bootstrap_servers=["{{ KAFKA_BROKER }}"],
    value_serializer=lambda v: json.dumps(v).encode()
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ingest")
def ingest_data(payload: dict):
    producer.send("ingest_topic", payload)
    producer.flush()
    logging.info("Data ingested: %s", payload)
    return {"message": "Data ingested"}
