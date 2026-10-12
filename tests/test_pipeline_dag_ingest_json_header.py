import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DAG_PATH = REPOSITORY_ROOT / "infra/airflow/dags/pipeline_dag.py"


class PipelineDagIngestJsonHeaderTests(unittest.TestCase):
    def test_run_ingest_curl_sends_json_content_type(self) -> None:
        source = DAG_PATH.read_text()
        ingest_block = source.split("task_ingest = BashOperator(", 1)[1].split(")", 1)[0]
        self.assertIn("http://kafka-ingest:8000/ingest", ingest_block)
        self.assertIn('Content-Type: application/json', ingest_block)
        self.assertIn('{"sample": "data"}', ingest_block)


if __name__ == "__main__":
    unittest.main()
