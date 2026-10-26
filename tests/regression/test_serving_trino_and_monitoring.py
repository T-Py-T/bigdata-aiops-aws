import unittest

from tests.regression.support import read_repo_file


class ServingTrinoAndMonitoringTests(unittest.TestCase):
    def test_trino_coordinator_is_enabled_with_http_port(self):
        config = read_repo_file("services/serving_trino/config/config.properties")
        required = {
            "coordinator=true",
            "node-scheduler.include-coordinator=true",
            "http-server.http.port=8080",
            "discovery.uri=http://localhost:8080",
        }
        lines = {line.strip() for line in config.splitlines() if line.strip()}
        self.assertTrue(required.issubset(lines))

    def test_base_kustomization_includes_observability_manifests(self):
        kustomization = read_repo_file("infra/k8s/base/kustomization.yaml")
        self.assertIn("- prometheus.yaml", kustomization)
        self.assertIn("- grafana.yaml", kustomization)

    def test_prometheus_selects_pipeline_service_monitors(self):
        prometheus = read_repo_file("infra/k8s/base/prometheus.yaml")
        self.assertRegex(prometheus, r"kind:\s*Prometheus")
        self.assertIn("team: data-pipeline", prometheus)

    def test_grafana_service_exposes_ui_port(self):
        grafana = read_repo_file("infra/k8s/base/grafana.yaml")
        self.assertRegex(grafana, r"kind:\s*Service")
        self.assertIn("port: 3000", grafana)
        self.assertIn("targetPort: 3000", grafana)


if __name__ == "__main__":
    unittest.main()
