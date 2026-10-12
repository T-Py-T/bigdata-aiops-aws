import subprocess
import unittest
from pathlib import Path

from support import REPOSITORY_ROOT


class TerraformScriptTests(unittest.TestCase):
    def setUp(self):
        self.terraform_dir = REPOSITORY_ROOT / "infra" / "terraform"

    def test_deploy_script_requires_command(self):
        result = subprocess.run(
            ["bash", str(self.terraform_dir / "deploy.sh")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Usage:", result.stdout)

    def test_deploy_and_destroy_use_chdir(self):
        for script_name in ("deploy.sh", "destroy.sh"):
            script = (self.terraform_dir / script_name).read_text()
            self.assertIn('-chdir="$terraform_directory"', script, script_name)

    def test_deploy_rejects_unknown_command_before_terraform(self):
        result = subprocess.run(
            ["bash", str(self.terraform_dir / "deploy.sh"), "invalid"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Unknown command: invalid", result.stdout)
        self.assertNotIn("Initializing", result.stderr)


if __name__ == "__main__":
    unittest.main()
