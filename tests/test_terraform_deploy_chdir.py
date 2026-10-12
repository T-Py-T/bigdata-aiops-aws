import re
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEPLOY_SCRIPT = REPOSITORY_ROOT / "infra/terraform/deploy.sh"


class TerraformDeployChdirTests(unittest.TestCase):
    def test_deploy_script_runs_terraform_from_its_directory(self) -> None:
        script = DEPLOY_SCRIPT.read_text()
        self.assertIn('terraform_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"', script)
        for match in re.finditer(r"terraform\s+(-chdir=\S+\s+)?\w+", script):
            self.assertIsNotNone(match.group(1), "every terraform invocation must use -chdir")


if __name__ == "__main__":
    unittest.main()
