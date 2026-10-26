import subprocess
import unittest
from pathlib import Path

from infra.support import REPOSITORY_ROOT

DEPLOY_SCRIPT = REPOSITORY_ROOT / "infra" / "terraform" / "deploy.sh"


class TerraformDeployScriptTests(unittest.TestCase):
    def test_deploy_script_passes_bash_syntax_check(self):
        result = subprocess.run(
            ["bash", "-n", str(DEPLOY_SCRIPT)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_deploy_script_requires_single_argument(self):
        result = subprocess.run(
            ["bash", str(DEPLOY_SCRIPT)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Usage:", result.stdout)

    def test_deploy_script_rejects_unknown_command(self):
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            terraform_path = Path(temp_dir) / "terraform"
            terraform_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            terraform_path.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{temp_dir}:{env.get('PATH', '')}"
            result = subprocess.run(
                ["bash", str(DEPLOY_SCRIPT), "plan"],
                capture_output=True,
                text=True,
                check=False,
                env=env,
                cwd=str(DEPLOY_SCRIPT.parent),
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Unknown command: plan", result.stdout)

    def test_deploy_script_documents_deploy_and_destroy_paths(self):
        content = DEPLOY_SCRIPT.read_text()
        self.assertIn('if [ "$COMMAND" == "deploy" ]; then', content)
        self.assertIn("terraform plan -out=tfplan", content)
        self.assertIn("terraform apply -auto-approve tfplan", content)
        self.assertIn('elif [ "$COMMAND" == "destroy" ]; then', content)
        self.assertIn("terraform destroy -auto-approve", content)


if __name__ == "__main__":
    unittest.main()
