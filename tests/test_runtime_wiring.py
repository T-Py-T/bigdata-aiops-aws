import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class RuntimeWiringTests(unittest.TestCase):
    def test_airflow_ingest_task_posts_json(self):
        dag_source = (
            REPOSITORY_ROOT / "infra" / "airflow" / "dags" / "pipeline_dag.py"
        ).read_text()
        self.assertIn("Content-Type: application/json", dag_source)
        self.assertRegex(
            dag_source,
            r"bash_command\s*=\s*\(",
            "ingest curl should be a parenthesized multi-line command",
        )

    def test_spark_deployments_match_image_entrypoint(self):
        spark_services = (
            ("spark_batch_processor", "batch_processor.py"),
            ("realtime_processor", "realtime_processor.py"),
        )
        for service_name, script_name in spark_services:
            deployment = (
                REPOSITORY_ROOT
                / "infra"
                / "k8s"
                / "base"
                / f"{service_name}-deployment.yaml"
            ).read_text()
            dockerfile = (
                REPOSITORY_ROOT / "services" / service_name / "Dockerfile"
            ).read_text()
            expected_cmd = f'["/opt/spark/bin/spark-submit", "{script_name}"]'
            self.assertIn(
                f"command: {expected_cmd}",
                deployment,
                f"{service_name} deployment must invoke spark-submit like the image CMD",
            )
            self.assertIn(
                f'CMD ["/opt/spark/bin/spark-submit", "{script_name}"]',
                dockerfile,
            )

    def test_generator_emits_same_spark_and_ingest_wiring(self):
        generator = (REPOSITORY_ROOT / "create_project.sh").read_text()
        self.assertIn('command: ["/opt/spark/bin/spark-submit", "batch_processor.py"]', generator)
        self.assertIn('command: ["/opt/spark/bin/spark-submit", "realtime_processor.py"]', generator)
        self.assertIn("Content-Type: application/json", generator)


if __name__ == "__main__":
    unittest.main()
