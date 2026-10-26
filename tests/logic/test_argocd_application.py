import unittest
from pathlib import Path

from .support import REPOSITORY_ROOT

APPLICATION = REPOSITORY_ROOT / "infra" / "argo-cd" / "application.yaml"


class ArgoCdApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = APPLICATION.read_text()

    def test_application_targets_dev_overlay(self):
        self.assertIn('path: "infra/k8s/overlays/dev"', self.manifest)

    def test_automated_sync_enables_prune_and_self_heal(self):
        self.assertIn("automated:", self.manifest)
        self.assertIn("prune: true", self.manifest)
        self.assertIn("selfHeal: true", self.manifest)

    def test_placeholders_remain_for_repo_and_cluster(self):
        self.assertIn('repoURL: "{{ REPO_URL }}"', self.manifest)
        self.assertIn('server: "{{ K8S_API_SERVER }}"', self.manifest)


if __name__ == "__main__":
    unittest.main()
