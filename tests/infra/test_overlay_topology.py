import re
import unittest
from pathlib import Path

from infra.support import REPOSITORY_ROOT

OVERLAYS = REPOSITORY_ROOT / "infra" / "k8s" / "overlays"
EXPECTED_REPLICAS = {
    "dev": 1,
    "qa": 2,
    "stage": 2,
    "prod": 3,
}
EXPECTED_TAGS = {
    "dev": "dev",
    "qa": "qa",
    "stage": "stage",
    "prod": "prod",
}


def _replica_counts(patch_text: str) -> list[int]:
    return [int(value) for value in re.findall(r"replicas:\s*(\d+)", patch_text)]


class OverlayTopologyTests(unittest.TestCase):
    def test_each_overlay_points_at_base_and_strategic_merge_patch(self):
        for environment in EXPECTED_REPLICAS:
            overlay_dir = OVERLAYS / environment
            kustomization = (overlay_dir / "kustomization.yaml").read_text()
            self.assertIn("../../base", kustomization, environment)
            self.assertIn("patchesStrategicMerge:", kustomization, environment)
            self.assertTrue((overlay_dir / "patch.yaml").is_file(), environment)

    def test_overlay_image_tags_match_environment(self):
        for environment, tag in EXPECTED_TAGS.items():
            kustomization = (OVERLAYS / environment / "kustomization.yaml").read_text()
            self.assertIn(f'newTag: "{tag}"', kustomization, environment)

    def test_replica_counts_scale_with_environment_tier(self):
        for environment, expected in EXPECTED_REPLICAS.items():
            patch = (OVERLAYS / environment / "patch.yaml").read_text()
            replicas = _replica_counts(patch)
            self.assertTrue(replicas, environment)
            self.assertTrue(
                all(count == expected for count in replicas),
                f"{environment} expected uniform replicas={expected}, got {replicas}",
            )

    def test_prod_overlay_tags_all_ten_service_images(self):
        kustomization = (OVERLAYS / "prod" / "kustomization.yaml").read_text()
        image_blocks = re.findall(
            r"- name: \{\{ ([A-Z0-9_]+) \}\}",
            kustomization,
        )
        self.assertEqual(len(image_blocks), 10)
        self.assertIn("SPARK_BATCH_PROCESSOR_IMAGE", image_blocks)
        self.assertIn("REALTIME_PROCESSOR_IMAGE", image_blocks)


if __name__ == "__main__":
    unittest.main()
