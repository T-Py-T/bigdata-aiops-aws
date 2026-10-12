import unittest

from tests.guards.support import deployment_replica_map, overlay_names, read_repo_text

EXPECTED_DEPLOYMENTS = (
    "kafka-ingest",
    "python-stream-processor",
    "spark-batch-processor",
    "realtime-processor",
    "ksqdb-connector",
    "serving-trino",
    "visualization-superset",
    "visualization-metabase",
    "data-catalog",
    "airflow",
)

OVERLAY_REPLICAS = {
    "dev": 1,
    "qa": 2,
    "stage": 2,
    "prod": 3,
}


class OverlayReplicaMatrixTests(unittest.TestCase):
    def test_each_overlay_patches_every_workload_with_expected_replicas(self):
        for overlay in overlay_names():
            patch = read_repo_text("infra", "k8s", "overlays", overlay, "patch.yaml")
            replicas = deployment_replica_map(patch)
            self.assertEqual(set(replicas), set(EXPECTED_DEPLOYMENTS), overlay)
            for deployment in EXPECTED_DEPLOYMENTS:
                self.assertEqual(
                    replicas[deployment],
                    OVERLAY_REPLICAS[overlay],
                    f"{overlay}:{deployment}",
                )


if __name__ == "__main__":
    unittest.main()
