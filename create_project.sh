#!/bin/bash
# Create directories
dirs=(
  "services/kafka_ingest/src"
  "services/kafka_ingest"
  "services/python_stream_processor/src"
  "services/python_stream_processor"
  "services/spark_batch_processor/src"
  "services/spark_batch_processor"
  "services/realtime_processor/src"
  "services/realtime_processor"
  "services/ksqdb_connector/src"
  "services/ksqdb_connector"
  "services/serving_trino/config"
  "services/serving_trino"
  "services/visualization_superset/config"
  "services/visualization_superset"
  "services/visualization_metabase/config"
  "services/visualization_metabase"
  "services/data_catalog/config"
  "services/data_catalog"
  "infra/k8s/base"
  "infra/k8s/overlays/dev"
  "infra/argo-cd"
  "infra/airflow/dags"
  "infra/airflow"
)

for d in "${dirs[@]}"; do
  mkdir -p "$d"
done

#####################################
# Services: Kafka Ingest
#####################################

cat << 'EOF' > services/kafka_ingest/src/ingest.py
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
EOF

cat << 'EOF' > services/kafka_ingest/Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .
CMD ["uvicorn", "ingest:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat << 'EOF' > services/kafka_ingest/requirements.txt
fastapi==0.95.1
uvicorn==0.21.1
kafka-python==2.0.2
EOF

#####################################
# Services: Python Stream Processor
#####################################

cat << 'EOF' > services/python_stream_processor/src/processor.py
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
EOF

cat << 'EOF' > services/python_stream_processor/Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .
CMD ["python", "processor.py"]
EOF

cat << 'EOF' > services/python_stream_processor/requirements.txt
kafka-python==2.0.2
EOF

#####################################
# Services: Spark Batch Processor (S3)
#####################################

cat << 'EOF' > services/spark_batch_processor/src/batch_processor.py
from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder.appName("SparkBatchProcessor").getOrCreate()
    s3_bucket = "s3a://{{ S3_BUCKET }}"
    df = spark.read.parquet(s3_bucket)
    df_transformed = df.filter("column IS NOT NULL")
    df_transformed.show()
    spark.stop()

if __name__ == "__main__":
    main()
EOF

cat << 'EOF' > services/spark_batch_processor/Dockerfile
FROM bitnami/spark:3.3.0-debian-11-r0
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .
CMD ["python", "batch_processor.py"]
EOF

cat << 'EOF' > services/spark_batch_processor/requirements.txt
pyspark==3.3.0
EOF

#####################################
# Services: Realtime Processor (Spark Structured Streaming)
#####################################

cat << 'EOF' > services/realtime_processor/src/realtime_processor.py
from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder.appName("RealtimeProcessor").getOrCreate()
    s3_bucket = "s3a://{{ S3_BUCKET }}"
    df = spark.readStream.format("parquet").load(s3_bucket)
    query = df.writeStream.format("console").start()
    query.awaitTermination()

if __name__ == "__main__":
    main()
EOF

cat << 'EOF' > services/realtime_processor/Dockerfile
FROM bitnami/spark:3.3.0-debian-11-r0
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .
CMD ["python", "realtime_processor.py"]
EOF

cat << 'EOF' > services/realtime_processor/requirements.txt
pyspark==3.3.0
EOF

#####################################
# Services: ksqDB Connector to Pinot & Elastic
#####################################

cat << 'EOF' > services/ksqdb_connector/src/connector.py
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
EOF

cat << 'EOF' > services/ksqdb_connector/Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .
CMD ["python", "connector.py"]
EOF

cat << 'EOF' > services/ksqdb_connector/requirements.txt
requests==2.28.1
EOF

#####################################
# Services: Trino Serving
#####################################

cat << 'EOF' > services/serving_trino/config/trino-config.yaml
coordinator: true
node-scheduler.include-coordinator: true
http-server.http.port: 8080
query.max-memory: 5GB
query.max-memory-per-node: 1GB
discovery-server.enabled: true
discovery.uri: "http://localhost:8080"
EOF

cat << 'EOF' > services/serving_trino/Dockerfile
FROM trinodb/trino:latest
COPY config/trino-config.yaml /etc/trino/config.properties
EOF

#####################################
# Services: Visualization – Superset
#####################################

cat << 'EOF' > services/visualization_superset/config/superset-config.yaml
SUPERSET_CONFIG_PATH: /app/superset_config.py
EOF

cat << 'EOF' > services/visualization_superset/Dockerfile
FROM apache/superset:latest
COPY config/superset-config.yaml /app/superset-config.yaml
EOF

#####################################
# Services: Visualization – Metabase
#####################################

cat << 'EOF' > services/visualization_metabase/config/metabase-config.yaml
metabase:
  config: /app/metabase_config.yml
EOF

cat << 'EOF' > services/visualization_metabase/Dockerfile
FROM metabase/metabase:latest
COPY config/metabase-config.yaml /app/metabase-config.yaml
EOF

#####################################
# Services: Data Catalog (DataHub)
#####################################

cat << 'EOF' > services/data_catalog/config/datahub-config.yaml
DATAHUB_GMS_URL: "http://datahub-gms:8080"
DATAHUB_ELASTIC_HOST: "http://{{ ELASTIC_ENDPOINT }}:9200"
EOF

cat << 'EOF' > services/data_catalog/Dockerfile
FROM datahub/datahub-frontend:latest
COPY config/datahub-config.yaml /app/datahub-config.yaml
EOF

#####################################
# Infra: Kubernetes Base Manifests
#####################################

# kafka_ingest deployment
cat << 'EOF' > infra/k8s/base/kafka_ingest-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka-ingest
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kafka-ingest
  template:
    metadata:
      labels:
        app: kafka-ingest
    spec:
      containers:
      - name: kafka-ingest
        image: "{{ KAFKA_INGEST_IMAGE }}"
        ports:
        - containerPort: 8000
        env:
          - name: KAFKA_BROKER
            value: "{{ KAFKA_BROKER }}"
EOF

# python_stream_processor deployment
cat << 'EOF' > infra/k8s/base/python_stream_processor-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-stream-processor
spec:
  replicas: 1
  selector:
    matchLabels:
      app: python-stream-processor
  template:
    metadata:
      labels:
        app: python-stream-processor
    spec:
      containers:
      - name: python-stream-processor
        image: "{{ PYTHON_STREAM_PROCESSOR_IMAGE }}"
        command: ["python", "processor.py"]
EOF

# spark_batch_processor deployment
cat << 'EOF' > infra/k8s/base/spark_batch_processor-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spark-batch-processor
spec:
  replicas: 1
  selector:
    matchLabels:
      app: spark-batch-processor
  template:
    metadata:
      labels:
        app: spark-batch-processor
    spec:
      containers:
      - name: spark-batch-processor
        image: "{{ SPARK_BATCH_PROCESSOR_IMAGE }}"
        command: ["python", "batch_processor.py"]
EOF

# realtime_processor deployment
cat << 'EOF' > infra/k8s/base/realtime_processor-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: realtime-processor
spec:
  replicas: 1
  selector:
    matchLabels:
      app: realtime-processor
  template:
    metadata:
      labels:
        app: realtime-processor
    spec:
      containers:
      - name: realtime-processor
        image: "{{ REALTIME_PROCESSOR_IMAGE }}"
        command: ["python", "realtime_processor.py"]
EOF

# ksqdb_connector deployment
cat << 'EOF' > infra/k8s/base/ksqdb_connector-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ksqdb-connector
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ksqdb-connector
  template:
    metadata:
      labels:
        app: ksqdb-connector
    spec:
      containers:
      - name: ksqdb-connector
        image: "{{ KSQLDB_CONNECTOR_IMAGE }}"
        command: ["python", "connector.py"]
EOF

# serving_trino deployment
cat << 'EOF' > infra/k8s/base/serving_trino-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: serving-trino
spec:
  replicas: 1
  selector:
    matchLabels:
      app: serving-trino
  template:
    metadata:
      labels:
        app: serving-trino
    spec:
      containers:
      - name: serving-trino
        image: "{{ SERVING_TRINO_IMAGE }}"
EOF

# visualization_superset deployment
cat << 'EOF' > infra/k8s/base/visualization_superset-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: visualization-superset
spec:
  replicas: 1
  selector:
    matchLabels:
      app: visualization-superset
  template:
    metadata:
      labels:
        app: visualization-superset
    spec:
      containers:
      - name: visualization-superset
        image: "{{ VISUALIZATION_SUPERSET_IMAGE }}"
EOF

# visualization_metabase deployment
cat << 'EOF' > infra/k8s/base/visualization_metabase-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: visualization-metabase
spec:
  replicas: 1
  selector:
    matchLabels:
      app: visualization-metabase
  template:
    metadata:
      labels:
        app: visualization-metabase
    spec:
      containers:
      - name: visualization-metabase
        image: "{{ VISUALIZATION_METABASE_IMAGE }}"
EOF

# data_catalog deployment
cat << 'EOF' > infra/k8s/base/data_catalog-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-catalog
spec:
  replicas: 1
  selector:
    matchLabels:
      app: data-catalog
  template:
    metadata:
      labels:
        app: data-catalog
    spec:
      containers:
      - name: data-catalog
        image: "{{ DATA_CATALOG_IMAGE }}"
EOF

# airflow deployment
cat << 'EOF' > infra/k8s/base/airflow-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: airflow
  template:
    metadata:
      labels:
        app: airflow
    spec:
      containers:
      - name: airflow
        image: "{{ AIRFLOW_IMAGE }}"
EOF

# Prometheus manifest
cat << 'EOF' > infra/k8s/base/prometheus.yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: prometheus
spec:
  serviceAccountName: prometheus
  serviceMonitorSelector:
    matchLabels:
      team: data-pipeline
EOF

# Grafana manifest
cat << 'EOF' > infra/k8s/base/grafana.yaml
apiVersion: v1
kind: Service
metadata:
  name: grafana
spec:
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
EOF

# Base kustomization.yaml
cat << 'EOF' > infra/k8s/base/kustomization.yaml
resources:
  - kafka_ingest-deployment.yaml
  - python_stream_processor-deployment.yaml
  - spark_batch_processor-deployment.yaml
  - realtime_processor-deployment.yaml
  - ksqdb_connector-deployment.yaml
  - serving_trino-deployment.yaml
  - visualization_superset-deployment.yaml
  - visualization_metabase-deployment.yaml
  - data_catalog-deployment.yaml
  - airflow-deployment.yaml
  - prometheus.yaml
  - grafana.yaml

images:
  - name: {{ KAFKA_INGEST_IMAGE }}
    newName: {{ KAFKA_INGEST_IMAGE }}
    newTag: "latest"
  - name: {{ PYTHON_STREAM_PROCESSOR_IMAGE }}
    newName: {{ PYTHON_STREAM_PROCESSOR_IMAGE }}
    newTag: "latest"
  - name: {{ SPARK_BATCH_PROCESSOR_IMAGE }}
    newName: {{ SPARK_BATCH_PROCESSOR_IMAGE }}
    newTag: "latest"
  - name: {{ REALTIME_PROCESSOR_IMAGE }}
    newName: {{ REALTIME_PROCESSOR_IMAGE }}
    newTag: "latest"
  - name: {{ KSQLDB_CONNECTOR_IMAGE }}
    newName: {{ KSQLDB_CONNECTOR_IMAGE }}
    newTag: "latest"
  - name: {{ SERVING_TRINO_IMAGE }}
    newName: {{ SERVING_TRINO_IMAGE }}
    newTag: "latest"
  - name: {{ VISUALIZATION_SUPERSET_IMAGE }}
    newName: {{ VISUALIZATION_SUPERSET_IMAGE }}
    newTag: "latest"
  - name: {{ VISUALIZATION_METABASE_IMAGE }}
    newName: {{ VISUALIZATION_METABASE_IMAGE }}
    newTag: "latest"
  - name: {{ DATA_CATALOG_IMAGE }}
    newName: {{ DATA_CATALOG_IMAGE }}
    newTag: "latest"
  - name: {{ AIRFLOW_IMAGE }}
    newName: {{ AIRFLOW_IMAGE }}
    newTag: "latest"
EOF

#####################################
# Infra: Kubernetes Overlays (dev)
#####################################

cat << 'EOF' > infra/k8s/overlays/dev/kustomization.yaml
bases:
  - ../../base

patchesStrategicMerge:
  - patch.yaml

images:
  - name: {{ KAFKA_INGEST_IMAGE }}
    newTag: "dev"
  - name: {{ PYTHON_STREAM_PROCESSOR_IMAGE }}
    newTag: "dev"
  - name: {{ SPARK_BATCH_PROCESSOR_IMAGE }}
    newTag: "dev"
  - name: {{ REALTIME_PROCESSOR_IMAGE }}
    newTag: "dev"
  - name: {{ KSQLDB_CONNECTOR_IMAGE }}
    newTag: "dev"
  - name: {{ SERVING_TRINO_IMAGE }}
    newTag: "dev"
  - name: {{ VISUALIZATION_SUPERSET_IMAGE }}
    newTag: "dev"
  - name: {{ VISUALIZATION_METABASE_IMAGE }}
    newTag: "dev"
  - name: {{ DATA_CATALOG_IMAGE }}
    newTag: "dev"
  - name: {{ AIRFLOW_IMAGE }}
    newTag: "dev"
EOF

cat << 'EOF' > infra/k8s/overlays/dev/patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka-ingest
spec:
  replicas: 1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-stream-processor
spec:
  replicas: 1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spark-batch-processor
spec:
  replicas: 1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: realtime-processor
spec:
  replicas: 1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ksqdb-connector
spec:
  replicas: 1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: serving-trino
spec:
  replicas: 1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: visualization-superset
spec:
  replicas: 1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: visualization-metabase
spec:
  replicas: 1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-catalog
spec:
  replicas: 1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow
spec:
  replicas: 1
EOF

#####################################
# Infra: ArgoCD Application
#####################################

cat << 'EOF' > infra/argo-cd/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: data-pipeline-app
spec:
  project: default
  source:
    repoURL: "{{ REPO_URL }}"
    targetRevision: HEAD
    path: "infra/k8s/overlays/dev"
  destination:
    server: "{{ K8S_API_SERVER }}"
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
EOF

#####################################
# Infra: Airflow DAG and Dockerfile
#####################################

cat << 'EOF' > infra/airflow/dags/pipeline_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'data_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
)

task_ingest = BashOperator(
    task_id='run_ingest',
    bash_command='curl -X POST http://kafka-ingest:8000/ingest -d \'{"sample": "data"}\'',
    dag=dag
)

task_stream = BashOperator(
    task_id='run_stream_processor',
    bash_command='python /app/processor.py',
    dag=dag
)

task_batch = BashOperator(
    task_id='run_batch_processor',
    bash_command='spark-submit --master local /app/batch_processor.py',
    dag=dag
)

task_ingest >> task_stream >> task_batch
EOF

cat << 'EOF' > infra/airflow/Dockerfile
FROM apache/airflow:2.5.0-python3.9
COPY dags/ /opt/airflow/dags/
EOF

echo "Project scaffold created successfully."