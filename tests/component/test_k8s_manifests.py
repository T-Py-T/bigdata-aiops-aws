import re
import unittest
from pathlib import Path

from component.support import REPOSITORY_ROOT

K8S_BASE = REPOSITORY_ROOT / "infra" / "k8s" / "base"
OVERLAY_ENVIRONMENTS = ("dev", "qa", "stage", "prod")


class K8sManifestTests(unittest.TestCase):
    def test_base_kustomization_lists_existing_resources(self):
        kustomization = (K8S_BASE / "kustomization.yaml").read_text()
        resources = re.findall(r"^\s*-\s+(\S+\.yaml)\s*$", kustomization, re.MULTILINE)
        self.assertTrue(resources, "expected resources in base kustomization.yaml")
        for resource in resources:
            path = K8S_BASE / resource
            self.assertTrue(path.is_file(), f"missing manifest: {resource}")

    def test_service_deployments_declare_images_and_selectors(self):
        deployment_files = sorted(K8S_BASE.glob("*-deployment.yaml"))
        self.assertGreaterEqual(len(deployment_files), 8)
        for deployment_file in deployment_files:
            content = deployment_file.read_text()
            self.assertIn("kind: Deployment", content, deployment_file.name)
            self.assertRegex(
                content,
                r"image:\s*\"?\{\{ [A-Z0-9_]+_IMAGE \}\}\"?",
                deployment_file.name,
            )
            self.assertIn("matchLabels:", content, deployment_file.name)

    def test_kafka_ingest_exposes_http_port(self):
        content = (K8S_BASE / "kafka_ingest-deployment.yaml").read_text()
        self.assertIn("containerPort: 8000", content)
        self.assertIn("KAFKA_BROKER", content)

    def test_overlays_reference_base_and_patch(self):
        for environment in OVERLAY_ENVIRONMENTS:
            overlay_dir = REPOSITORY_ROOT / "infra" / "k8s" / "overlays" / environment
            kustomization = (overlay_dir / "kustomization.yaml").read_text()
            self.assertIn("../../base", kustomization, environment)
            self.assertTrue((overlay_dir / "patch.yaml").is_file(), environment)


class ArgoCdApplicationTests(unittest.TestCase):
    def test_application_targets_dev_overlay(self):
        content = (REPOSITORY_ROOT / "infra" / "argo-cd" / "application.yaml").read_text()
        self.assertIn('path: "infra/k8s/overlays/dev"', content)
        self.assertIn("automated:", content)
        self.assertIn("selfHeal: true", content)


if __name__ == "__main__":
    unittest.main()
