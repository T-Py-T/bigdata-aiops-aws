import re
import unittest
from pathlib import Path

from component.support import REPOSITORY_ROOT

PYTHON_REQUIREMENTS = (
    REPOSITORY_ROOT / "services" / "kafka_ingest" / "requirements.txt",
    REPOSITORY_ROOT / "services" / "ksqdb_connector" / "requirements.txt",
    REPOSITORY_ROOT / "services" / "python_stream_processor" / "requirements.txt",
)


class SupplyChainTests(unittest.TestCase):
    def test_python_requirements_use_exact_pins(self):
        pin_pattern = re.compile(r"^[a-zA-Z0-9_.-]+==[0-9]+\.[0-9]+")
        for requirements_file in PYTHON_REQUIREMENTS:
            lines = [
                line.strip()
                for line in requirements_file.read_text().splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            self.assertTrue(lines, str(requirements_file))
            for line in lines:
                self.assertRegex(
                    line,
                    pin_pattern,
                    f"{requirements_file.name} must pin versions: {line}",
                )

    def test_trino_config_sets_http_port(self):
        config = (
            REPOSITORY_ROOT / "services" / "serving_trino" / "config" / "config.properties"
        ).read_text()
        self.assertIn("http-server.http.port=8080", config)

    def test_dependabot_watches_github_actions(self):
        dependabot = (REPOSITORY_ROOT / ".github" / "dependabot.yml").read_text()
        self.assertIn("package-ecosystem: github-actions", dependabot)


if __name__ == "__main__":
    unittest.main()
