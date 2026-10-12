import unittest

from tests.guards.support import read_repo_text


class DestroyScriptTests(unittest.TestCase):
    def test_destroy_runs_terraform_from_script_directory(self):
        script = read_repo_text("infra", "terraform", "destroy.sh")

        self.assertIn('terraform_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"', script)
        self.assertIn('terraform -chdir="$terraform_directory" init', script)
        self.assertIn('terraform -chdir="$terraform_directory" destroy "$@"', script)

    def test_destroy_enables_strict_shell_options(self):
        script = read_repo_text("infra", "terraform", "destroy.sh")
        self.assertIn("set -euo pipefail", script)


if __name__ == "__main__":
    unittest.main()
