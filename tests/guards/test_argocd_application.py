import unittest

import yaml

from tests.guards.support import read_repo_text


class ArgoCdApplicationTests(unittest.TestCase):
    def test_application_targets_dev_overlay_with_automated_sync(self):
        document = yaml.safe_load(read_repo_text("infra", "argo-cd", "application.yaml"))

        self.assertEqual(document["kind"], "Application")
        self.assertEqual(document["metadata"]["name"], "data-pipeline-app")
        self.assertEqual(document["spec"]["source"]["path"], "infra/k8s/overlays/dev")
        self.assertEqual(document["spec"]["source"]["targetRevision"], "HEAD")

        automated = document["spec"]["syncPolicy"]["automated"]
        self.assertTrue(automated["prune"])
        self.assertTrue(automated["selfHeal"])


if __name__ == "__main__":
    unittest.main()
