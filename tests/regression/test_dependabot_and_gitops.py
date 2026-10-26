import re
import unittest

from tests.regression.support import read_repo_file


PIP_SERVICE_DIRECTORIES = (
    "/services/kafka_ingest",
    "/services/ksqdb_connector",
    "/services/python_stream_processor",
)


class DependabotAndGitopsTests(unittest.TestCase):
    def test_dependabot_tracks_all_python_services_and_infra(self):
        dependabot = read_repo_file(".github/dependabot.yml")
        for directory in PIP_SERVICE_DIRECTORIES:
            self.assertIn(f"directory: {directory}", dependabot)
        self.assertIn("package-ecosystem: terraform", dependabot)
        self.assertIn("directory: /infra/terraform", dependabot)
        self.assertIn("package-ecosystem: github-actions", dependabot)

    def test_dependabot_limits_open_pull_requests(self):
        dependabot = read_repo_file(".github/dependabot.yml")
        limits = re.findall(r"open-pull-requests-limit:\s*(\d+)", dependabot)
        self.assertTrue(limits)
        self.assertTrue(all(int(limit) <= 5 for limit in limits))

    def test_argocd_application_targets_dev_overlay_with_automation(self):
        application = read_repo_file("infra/argo-cd/application.yaml")
        self.assertIn('path: "infra/k8s/overlays/dev"', application)
        self.assertIn("repoURL: \"{{ REPO_URL }}\"", application)
        self.assertIn("prune: true", application)
        self.assertIn("selfHeal: true", application)


if __name__ == "__main__":
    unittest.main()
