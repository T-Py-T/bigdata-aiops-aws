import re
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
K8S_BASE = REPOSITORY_ROOT / "infra" / "k8s" / "base"


def _split_manifests(content: str) -> list[str]:
    return [document for document in content.split("---") if document.strip()]


class ClusterServiceEndpointTests(unittest.TestCase):
    def test_kafka_ingest_service_matches_airflow_dns_name_and_port(self):
        dag_source = (
            REPOSITORY_ROOT / "infra" / "airflow" / "dags" / "pipeline_dag.py"
        ).read_text()
        self.assertIn("http://kafka-ingest:8000/ingest", dag_source)

        content = (K8S_BASE / "kafka_ingest-deployment.yaml").read_text()
        documents = _split_manifests(content)
        service = next(
            doc for doc in documents if re.search(r"^kind:\s*Service", doc, re.MULTILINE)
        )
        deployment = next(
            doc
            for doc in documents
            if re.search(r"^kind:\s*Deployment", doc, re.MULTILINE)
        )

        service_name = re.search(r"^metadata:\s*\n\s*name:\s*(\S+)", service, re.MULTILINE)
        self.assertIsNotNone(service_name)
        self.assertEqual(service_name.group(1), "kafka-ingest")

        self.assertRegex(service, r"port:\s*8000")
        self.assertRegex(service, r"targetPort:\s*8000")
        self.assertRegex(service, r"selector:\s*\n\s*app:\s*kafka-ingest")

        self.assertRegex(deployment, r"containerPort:\s*8000")

    def test_serving_trino_service_exposes_coordinator_http_port(self):
        config = (
            REPOSITORY_ROOT / "services" / "serving_trino" / "config" / "config.properties"
        ).read_text()
        self.assertIn("http-server.http.port=8080", config)

        content = (K8S_BASE / "serving_trino-deployment.yaml").read_text()
        documents = _split_manifests(content)
        service = next(
            doc for doc in documents if re.search(r"^kind:\s*Service", doc, re.MULTILINE)
        )
        deployment = next(
            doc
            for doc in documents
            if re.search(r"^kind:\s*Deployment", doc, re.MULTILINE)
        )

        service_name = re.search(r"^metadata:\s*\n\s*name:\s*(\S+)", service, re.MULTILINE)
        self.assertIsNotNone(service_name)
        self.assertEqual(service_name.group(1), "serving-trino")

        self.assertRegex(service, r"port:\s*8080")
        self.assertRegex(service, r"targetPort:\s*8080")
        self.assertRegex(service, r"selector:\s*\n\s*app:\s*serving-trino")
        self.assertRegex(deployment, r"containerPort:\s*8080")


if __name__ == "__main__":
    unittest.main()
