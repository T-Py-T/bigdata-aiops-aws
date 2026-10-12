import unittest
from pathlib import Path

from .support import REPOSITORY_ROOT

DESTROY_SCRIPT = REPOSITORY_ROOT / "infra" / "terraform" / "destroy.sh"


class DestroyScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = DESTROY_SCRIPT.read_text()

    def test_destroy_runs_terraform_from_script_directory(self):
        self.assertIn('terraform_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"', self.script)
        self.assertIn('terraform -chdir="$terraform_directory" init', self.script)
        self.assertIn('terraform -chdir="$terraform_directory" destroy "$@"', self.script)

    def test_destroy_enables_strict_shell_options(self):
        self.assertIn("set -euo pipefail", self.script)


if __name__ == "__main__":
    unittest.main()
