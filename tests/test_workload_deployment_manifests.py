import re
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
K8S_BASE = REPOSITORY_ROOT / "infra" / "k8s" / "base"


class WorkloadDeploymentManifestTests(unittest.TestCase):
    def read_deployment_manifest(self, filename: str) -> str:
        content = (K8S_BASE / filename).read_text()
        self.assertIn("kind: Deployment", content)
        return content

    def test_python_stream_processor_runs_processor_entrypoint(self) -> None:
        deployment = self.read_deployment_manifest("python_stream_processor-deployment.yaml")
        dockerfile = (
            REPOSITORY_ROOT / "services/python_stream_processor/Dockerfile"
        ).read_text()
        self.assertIn('command: ["python", "processor.py"]', deployment)
        self.assertIn('CMD ["python", "processor.py"]', dockerfile)
        self.assertRegex(deployment, r'image:\s*"\{\{ PYTHON_STREAM_PROCESSOR_IMAGE \}\}"')

    def test_spark_batch_processor_runs_batch_entrypoint(self) -> None:
        deployment = self.read_deployment_manifest("spark_batch_processor-deployment.yaml")
        dockerfile = (
            REPOSITORY_ROOT / "services/spark_batch_processor/Dockerfile"
        ).read_text()
        self.assertIn('command: ["python", "batch_processor.py"]', deployment)
        self.assertIn("spark-submit", dockerfile)
        self.assertIn("batch_processor.py", dockerfile)
        self.assertRegex(deployment, r'image:\s*"\{\{ SPARK_BATCH_PROCESSOR_IMAGE \}\}"')

    def test_realtime_processor_runs_streaming_entrypoint(self) -> None:
        deployment = self.read_deployment_manifest("realtime_processor-deployment.yaml")
        self.assertIn('command: ["python", "realtime_processor.py"]', deployment)
        self.assertRegex(deployment, r'image:\s*"\{\{ REALTIME_PROCESSOR_IMAGE \}\}"')

    def test_ksqdb_connector_runs_connector_entrypoint(self) -> None:
        deployment = self.read_deployment_manifest("ksqdb_connector-deployment.yaml")
        dockerfile = (REPOSITORY_ROOT / "services/ksqdb_connector/Dockerfile").read_text()
        self.assertIn('command: ["python", "connector.py"]', deployment)
        self.assertIn('CMD ["python", "connector.py"]', dockerfile)

    def test_data_catalog_uses_datahub_frontend_image_placeholder(self) -> None:
        deployment = self.read_deployment_manifest("data_catalog-deployment.yaml")
        dockerfile = (REPOSITORY_ROOT / "services/data_catalog/Dockerfile").read_text()
        self.assertRegex(deployment, r'image:\s*"\{\{ DATA_CATALOG_IMAGE \}\}"')
        self.assertIn("datahub-frontend-react", dockerfile)

    def test_airflow_deployment_references_airflow_image_placeholder(self) -> None:
        deployment = self.read_deployment_manifest("airflow-deployment.yaml")
        dockerfile = (REPOSITORY_ROOT / "infra/airflow/Dockerfile").read_text()
        self.assertRegex(deployment, r'image:\s*"\{\{ AIRFLOW_IMAGE \}\}"')
        self.assertIn("apache/airflow", dockerfile)

    def test_visualization_superset_mounts_platform_secret(self) -> None:
        deployment = self.read_deployment_manifest("visualization_superset-deployment.yaml")
        self.assertIn("SUPERSET_SECRET_KEY", deployment)
        self.assertIn("bigdata-platform-secrets", deployment)
        self.assertIn("superset-secret-key", deployment)

    def test_kustomization_lists_all_workload_manifests(self) -> None:
        kustomization = (K8S_BASE / "kustomization.yaml").read_text()
        expected_resources = (
            "kafka_ingest-deployment.yaml",
            "python_stream_processor-deployment.yaml",
            "spark_batch_processor-deployment.yaml",
            "realtime_processor-deployment.yaml",
            "ksqdb_connector-deployment.yaml",
            "serving_trino-deployment.yaml",
            "visualization_superset-deployment.yaml",
            "visualization_metabase-deployment.yaml",
            "data_catalog-deployment.yaml",
            "airflow-deployment.yaml",
        )
        for resource in expected_resources:
            self.assertIn(f"- {resource}", kustomization)


if __name__ == "__main__":
    unittest.main()
