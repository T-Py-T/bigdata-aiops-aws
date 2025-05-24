import logging
import requests

def push_to_pinot(data):
    logging.info("Pushing data to Pinot: %s", data)
    # requests.post("http://{{ PINOT_ENDPOINT }}/ingest", json=data)

def push_to_elastic(data):
    logging.info("Pushing data to Elastic: %s", data)
    # requests.post("http://{{ ELASTIC_ENDPOINT }}/index", json=data)

if __name__ == "__main__":
    sample_data = {"key": "value"}
    push_to_pinot(sample_data)
    push_to_elastic(sample_data)
