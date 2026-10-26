import re
import unittest
from pathlib import Path

from .support import REPOSITORY_ROOT

VARIABLES_TF = REPOSITORY_ROOT / "infra" / "terraform" / "variables.tf"


def _numeric_defaults(source: str) -> dict[str, int]:
    pattern = re.compile(
        r'variable\s+"(?P<name>[^"]+)"\s*\{[^}]*default\s*=\s*(?P<value>\d+)',
        re.MULTILINE | re.DOTALL,
    )
    return {match.group("name"): int(match.group("value")) for match in pattern.finditer(source)}


def _string_defaults(source: str) -> dict[str, str]:
    pattern = re.compile(
        r'variable\s+"(?P<name>[^"]+)"\s*\{[^}]*default\s*=\s*"(?P<value>[^"]+)"',
        re.MULTILINE | re.DOTALL,
    )
    return {match.group("name"): match.group("value") for match in pattern.finditer(source)}


class TerraformVariableDefaultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.variables_source = VARIABLES_TF.read_text()

    def test_cluster_version_default_is_pinned(self):
        defaults = _string_defaults(self.variables_source)
        self.assertEqual(defaults["cluster_version"], "1.35")

    def test_node_capacity_defaults_are_ordered(self):
        defaults = _numeric_defaults(self.variables_source)
        self.assertLessEqual(defaults["min_capacity"], defaults["desired_capacity"])
        self.assertLessEqual(defaults["desired_capacity"], defaults["max_capacity"])

    def test_instance_type_default_is_t3_medium(self):
        defaults = _string_defaults(self.variables_source)
        self.assertEqual(defaults["instance_type"], "t3.medium")


if __name__ == "__main__":
    unittest.main()
