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
