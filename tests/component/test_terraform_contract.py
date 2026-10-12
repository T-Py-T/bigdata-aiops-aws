import re
import subprocess
import unittest
from pathlib import Path

from component.support import REPOSITORY_ROOT

TERRAFORM_DIR = REPOSITORY_ROOT / "infra" / "terraform"


class TerraformContractTests(unittest.TestCase):
    def test_required_providers_are_pinned(self):
        main_tf = (TERRAFORM_DIR / "main.tf").read_text()
        self.assertRegex(main_tf, r'version\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+"')
        self.assertIn('source  = "hashicorp/aws"', main_tf)

    def test_eks_and_vpc_modules_use_explicit_versions(self):
        main_tf = (TERRAFORM_DIR / "main.tf").read_text()
        self.assertIn('module "vpc"', main_tf)
        self.assertIn('module "eks"', main_tf)
        module_versions = re.findall(
            r'module\s+"[^"]+"\s*\{[^}]*version\s*=\s*"([^"]+)"',
            main_tf,
            re.DOTALL,
        )
        self.assertEqual(len(module_versions), 2)
        for version in module_versions:
            self.assertRegex(version, r"^[0-9]+\.[0-9]+\.[0-9]+$")

    def test_outputs_reference_declared_modules(self):
        outputs = (TERRAFORM_DIR / "outputs.tf").read_text()
        for output_name in (
            "vpc_id",
            "public_subnets",
            "private_subnets",
            "eks_cluster_name",
            "eks_cluster_endpoint",
            "alb_dns_name",
        ):
            self.assertIn(f'output "{output_name}"', outputs)

    def test_variables_without_defaults_are_documented(self):
        variables_tf = (TERRAFORM_DIR / "variables.tf").read_text()
        blocks = re.findall(
            r'variable\s+"([^"]+)"\s*\{([^}]+)\}',
            variables_tf,
            re.DOTALL,
        )
        required = [
            name
            for name, body in blocks
            if "default" not in body and name not in {"cluster_version", "instance_type"}
        ]
        for name, body in blocks:
            if name in required or "default" not in body:
                self.assertIn("description", body, f"variable {name} missing description")

    def test_destroy_script_is_strict_bash(self):
        result = subprocess.run(
            ["bash", "-n", str(TERRAFORM_DIR / "destroy.sh")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
