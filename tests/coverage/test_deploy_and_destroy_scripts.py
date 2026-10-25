import subprocess
import unittest
from pathlib import Path

from tests.coverage.support import REPOSITORY_ROOT, read_repo_file


class DeployAndDestroyScriptTests(unittest.TestCase):
    def test_shell_scripts_pass_bash_syntax_check(self) -> None:
        scripts = (
            REPOSITORY_ROOT / "infra/terraform/deploy.sh",
            REPOSITORY_ROOT / "infra/terraform/destroy.sh",
        )
        for script in scripts:
            completed = subprocess.run(
                ["bash", "-n", str(script)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, script.name)

    def test_deploy_script_requires_single_command_argument(self) -> None:
        deploy = read_repo_file("infra", "terraform", "deploy.sh")
        self.assertIn('if [ "$#" -ne 1 ]; then', deploy)
        self.assertIn("Usage: $0 [deploy|destroy]", deploy)
        self.assertIn('elif [ "$COMMAND" == "destroy" ]; then', deploy)
        self.assertIn("terraform apply -auto-approve tfplan", deploy)
        self.assertIn("terraform destroy -auto-approve", deploy)

    def test_destroy_script_runs_terraform_from_script_directory(self) -> None:
        destroy = read_repo_file("infra", "terraform", "destroy.sh")
        self.assertIn("set -euo pipefail", destroy)
        self.assertIn('terraform -chdir="$terraform_directory" init', destroy)
        self.assertIn('terraform -chdir="$terraform_directory" destroy "$@"', destroy)


if __name__ == "__main__":
    unittest.main()
