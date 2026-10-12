import re
import unittest
from pathlib import Path

from tests.coverage.support import REPOSITORY_ROOT, read_repo_file


class DependabotEcosystemPathTests(unittest.TestCase):
    def test_configured_directories_exist_on_disk(self) -> None:
        dependabot = read_repo_file(".github", "dependabot.yml")
        directories = re.findall(r"directory:\s*(\S+)", dependabot)
        self.assertGreaterEqual(len(directories), 5)
        for directory in directories:
            path = REPOSITORY_ROOT / directory.lstrip("/")
            self.assertTrue(path.is_dir(), directory)

    def test_python_services_and_terraform_are_represented(self) -> None:
        dependabot = read_repo_file(".github", "dependabot.yml")
        self.assertIn("package-ecosystem: pip", dependabot)
        self.assertIn("package-ecosystem: terraform", dependabot)
        self.assertIn("package-ecosystem: github-actions", dependabot)
        self.assertIn("directory: /infra/terraform", dependabot)


class PreCommitHookTests(unittest.TestCase):
    def test_pre_commit_runs_scaffold_tests_and_shell_checks(self) -> None:
        config = read_repo_file(".pre-commit-config.yaml")
        self.assertIn("python3 -m unittest discover -s tests -v", config)
        self.assertIn("bash -n create_project.sh infra/terraform/deploy.sh infra/terraform/destroy.sh", config)
        self.assertIn("terraform -chdir=infra/terraform fmt -check", config)


if __name__ == "__main__":
    unittest.main()
