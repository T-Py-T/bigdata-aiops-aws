import re
import unittest

from tests.coverage.support import read_repo_file


class K8sMonitoringAndServingManifestTests(unittest.TestCase):
    def test_prometheus_selects_pipeline_service_monitors(self) -> None:
        prometheus = read_repo_file("infra", "k8s", "base", "prometheus.yaml")
        self.assertIn("kind: Prometheus", prometheus)
        self.assertIn("serviceAccountName: prometheus", prometheus)
        self.assertIn("team: data-pipeline", prometheus)

    def test_grafana_service_exposes_ui_port(self) -> None:
        grafana = read_repo_file("infra", "k8s", "base", "grafana.yaml")
        self.assertIn("kind: Service", grafana)
        self.assertIn("name: grafana", grafana)
        self.assertIn("app: grafana", grafana)
        self.assertIn("port: 3000", grafana)
        self.assertIn("targetPort: 3000", grafana)

    def test_serving_trino_deployment_uses_trino_image_placeholder(self) -> None:
        deployment = read_repo_file(
            "infra", "k8s", "base", "serving_trino-deployment.yaml"
        )
        self.assertRegex(deployment, r'name:\s+serving-trino')
        self.assertRegex(deployment, r'image:\s*"\{\{ SERVING_TRINO_IMAGE \}\}"')
        self.assertIn("app: serving-trino", deployment)

    def test_visualization_metabase_deployment_matches_selector_labels(self) -> None:
        deployment = read_repo_file(
            "infra", "k8s", "base", "visualization_metabase-deployment.yaml"
        )
        names = set(re.findall(r"app:\s+(\S+)", deployment))
        self.assertEqual(names, {"visualization-metabase"})
        self.assertRegex(deployment, r'image:\s*"\{\{ VISUALIZATION_METABASE_IMAGE \}\}"')


if __name__ == "__main__":
    unittest.main()
