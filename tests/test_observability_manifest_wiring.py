import re
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
K8S_BASE = REPOSITORY_ROOT / "infra" / "k8s" / "base"


def _split_manifests(content: str) -> list[str]:
    return [document for document in content.split("---") if document.strip()]


class ObservabilityManifestWiringTests(unittest.TestCase):
    def test_prometheus_manifest_declares_matching_service_account(self):
        content = (K8S_BASE / "prometheus.yaml").read_text()
        documents = _split_manifests(content)
        kinds = {re.search(r"^kind:\s*(\S+)", doc, re.MULTILINE).group(1) for doc in documents}
        self.assertIn("ServiceAccount", kinds)
        self.assertIn("Prometheus", kinds)

        service_account = next(
            doc for doc in documents if re.search(r"^kind:\s*ServiceAccount", doc, re.MULTILINE)
        )
        prometheus = next(
            doc for doc in documents if re.search(r"^kind:\s*Prometheus", doc, re.MULTILINE)
        )
        account_name = re.search(r"^metadata:\s*\n\s*name:\s*(\S+)", service_account, re.MULTILINE)
        referenced = re.search(r"serviceAccountName:\s*(\S+)", prometheus)
        self.assertIsNotNone(account_name)
        self.assertIsNotNone(referenced)
        self.assertEqual(account_name.group(1), referenced.group(1))

    def test_grafana_service_selector_matches_deployment_pods(self):
        content = (K8S_BASE / "grafana.yaml").read_text()
        documents = _split_manifests(content)
        deployment = next(
            doc for doc in documents if re.search(r"^kind:\s*Deployment", doc, re.MULTILINE)
        )
        service = next(doc for doc in documents if re.search(r"^kind:\s*Service", doc, re.MULTILINE))

        deployment_labels = re.search(
            r"template:\s*\n\s*metadata:\s*\n\s*labels:\s*\n\s*app:\s*(\S+)",
            deployment,
            re.MULTILINE,
        )
        service_selector = re.search(
            r"selector:\s*\n\s*app:\s*(\S+)",
            service,
            re.MULTILINE,
        )
        self.assertIsNotNone(deployment_labels)
        self.assertIsNotNone(service_selector)
        self.assertEqual(deployment_labels.group(1), service_selector.group(1))

        self.assertRegex(deployment, r"containerPort:\s*3000")


if __name__ == "__main__":
    unittest.main()
