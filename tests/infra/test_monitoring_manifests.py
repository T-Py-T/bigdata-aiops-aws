import re
import unittest

from infra.support import REPOSITORY_ROOT

K8S_BASE = REPOSITORY_ROOT / "infra" / "k8s" / "base"


class MonitoringManifestTests(unittest.TestCase):
    def test_prometheus_selects_pipeline_service_monitors(self):
        content = (K8S_BASE / "prometheus.yaml").read_text()
        self.assertIn("kind: Prometheus", content)
        self.assertIn("serviceMonitorSelector:", content)
        self.assertIn("team: data-pipeline", content)

    def test_grafana_service_exposes_ui_port(self):
        content = (K8S_BASE / "grafana.yaml").read_text()
        self.assertIn("kind: Service", content)
        self.assertIn("name: grafana", content)
        self.assertRegex(content, r"port:\s*3000")
        self.assertRegex(content, r"targetPort:\s*3000")

    def test_base_kustomization_includes_observability_resources(self):
        kustomization = (K8S_BASE / "kustomization.yaml").read_text()
        self.assertIn("- prometheus.yaml", kustomization)
        self.assertIn("- grafana.yaml", kustomization)


if __name__ == "__main__":
    unittest.main()
