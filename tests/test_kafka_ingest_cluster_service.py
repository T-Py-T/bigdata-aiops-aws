import re
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
K8S_BASE = REPOSITORY_ROOT / "infra" / "k8s" / "base"


class KafkaIngestClusterServiceTests(unittest.TestCase):
    def test_service_manifest_exposes_port_8000_for_airflow_dns(self):
        service = (K8S_BASE / "kafka_ingest-service.yaml").read_text()
        self.assertIn("kind: Service", service)
        self.assertIn("name: kafka-ingest", service)
        self.assertRegex(service, r"port:\s*8000")
        self.assertRegex(service, r"targetPort:\s*8000")
        self.assertIn("app: kafka-ingest", service)

    def test_service_selector_matches_deployment_labels(self):
        deployment = (K8S_BASE / "kafka_ingest-deployment.yaml").read_text()
        service = (K8S_BASE / "kafka_ingest-service.yaml").read_text()
        deployment_labels = re.findall(r"app:\s*kafka-ingest", deployment)
        service_labels = re.findall(r"app:\s*kafka-ingest", service)
        self.assertTrue(deployment_labels)
        self.assertTrue(service_labels)

    def test_base_kustomization_includes_kafka_ingest_service(self):
        kustomization = (K8S_BASE / "kustomization.yaml").read_text()
        self.assertIn("- kafka_ingest-service.yaml", kustomization)
        self.assertTrue((K8S_BASE / "kafka_ingest-service.yaml").is_file())

    def test_airflow_ingest_task_targets_kafka_ingest_service_hostname(self):
        dag = (REPOSITORY_ROOT / "infra" / "airflow" / "dags" / "pipeline_dag.py").read_text()
        self.assertIn("http://kafka-ingest:8000/ingest", dag)


if __name__ == "__main__":
    unittest.main()
