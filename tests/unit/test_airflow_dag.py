import unittest
from pathlib import Path

from support import REPOSITORY_ROOT


class AirflowDagTests(unittest.TestCase):
    def setUp(self):
        self.dag_source = (
            REPOSITORY_ROOT / "infra" / "airflow" / "dags" / "pipeline_dag.py"
        ).read_text()

    def test_daily_schedule_and_task_chain(self):
        self.assertIn("schedule='@daily'", self.dag_source)
        self.assertIn("task_ingest >> task_stream >> task_batch", self.dag_source)

    def test_ingest_task_targets_kafka_service(self):
        self.assertIn("http://kafka-ingest:8000/ingest", self.dag_source)

    def test_batch_task_uses_spark_submit(self):
        self.assertIn("spark-submit --master local", self.dag_source)


if __name__ == "__main__":
    unittest.main()
