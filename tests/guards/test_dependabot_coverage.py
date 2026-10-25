import unittest

import yaml

from tests.guards.support import read_repo_text


class DependabotCoverageTests(unittest.TestCase):
    def test_dependabot_watches_python_terraform_and_github_actions(self):
        config = yaml.safe_load(read_repo_text(".github", "dependabot.yml"))
        ecosystems = {entry["package-ecosystem"] for entry in config["updates"]}
        self.assertEqual(ecosystems, {"pip", "terraform", "github-actions"})

        pip_directories = {
            entry["directory"]
            for entry in config["updates"]
            if entry["package-ecosystem"] == "pip"
        }
        self.assertEqual(
            pip_directories,
            {
                "/services/kafka_ingest",
                "/services/ksqdb_connector",
                "/services/python_stream_processor",
            },
        )


if __name__ == "__main__":
    unittest.main()
