import re
import unittest

from tests.regression.support import (
    EXPECTED_WORKLOAD_DEPLOYMENTS,
    OVERLAY_ENVIRONMENTS,
    OVERLAY_REPLICA_EXPECTATIONS,
    deployment_replicas_from_patch,
    read_repo_file,
)


class OverlayScalingMatrixTests(unittest.TestCase):
    def test_each_overlay_patches_every_workload_deployment(self):
        for environment in OVERLAY_ENVIRONMENTS:
            patch_path = f"infra/k8s/overlays/{environment}/patch.yaml"
            replicas = deployment_replicas_from_patch(read_repo_file(patch_path))
            self.assertEqual(
                set(replicas),
                set(EXPECTED_WORKLOAD_DEPLOYMENTS),
                environment,
            )

    def test_replica_counts_follow_environment_tier(self):
        for environment, expected_replicas in OVERLAY_REPLICA_EXPECTATIONS.items():
            patch_path = f"infra/k8s/overlays/{environment}/patch.yaml"
            replicas = deployment_replicas_from_patch(read_repo_file(patch_path))
            for deployment, count in replicas.items():
                self.assertEqual(
                    count,
                    expected_replicas,
                    f"{environment}/{deployment}",
                )

    def test_overlay_image_tags_match_environment_name(self):
        for environment in OVERLAY_ENVIRONMENTS:
            kustomization_path = (
                f"infra/k8s/overlays/{environment}/kustomization.yaml"
            )
            content = read_repo_file(kustomization_path)
            self.assertIn("bases:\n  - ../../base", content)
            tags = set(re.findall(r'newTag:\s*"([^"]+)"', content))
            self.assertEqual(tags, {environment})


if __name__ == "__main__":
    unittest.main()
