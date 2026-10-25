import re
import unittest

from tests.coverage.support import read_repo_file


class TerraformMainTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.main_tf = read_repo_file("infra", "terraform", "main.tf")

    def test_provider_and_module_versions_are_pinned(self) -> None:
        self.assertIn('required_version = ">= 1.5.7"', self.main_tf)
        self.assertRegex(
            self.main_tf,
            r'version\s*=\s*"6\.67\.0"',
        )
        self.assertRegex(self.main_tf, r'terraform-aws-modules/vpc/aws"\s*\n\s*version\s*=\s*"6\.7\.3"')
        self.assertRegex(self.main_tf, r'terraform-aws-modules/eks/aws"\s*\n\s*version\s*=\s*"21\.26\.0"')

    def test_eks_runs_on_private_subnets_with_managed_nodes(self) -> None:
        eks_block = re.search(r'module\s+"eks"\s*\{.*?\n\}', self.main_tf, re.DOTALL)
        self.assertIsNotNone(eks_block)
        eks = eks_block.group(0)
        self.assertIn("subnet_ids         = module.vpc.private_subnets", eks)
        self.assertIn("eks_managed_node_groups", eks)
        self.assertIn("desired_size   = var.desired_capacity", eks)

    def test_vpc_enables_single_nat_gateway(self) -> None:
        vpc_block = re.search(r'module\s+"vpc"\s*\{.*?\n\}', self.main_tf, re.DOTALL)
        self.assertIsNotNone(vpc_block)
        vpc = vpc_block.group(0)
        self.assertIn("enable_nat_gateway = true", vpc)
        self.assertIn("single_nat_gateway = true", vpc)

    def test_alb_is_public_and_allows_http_and_https(self) -> None:
        self.assertIn("load_balancer_type = \"application\"", self.main_tf)
        self.assertIn("subnets            = module.vpc.public_subnets", self.main_tf)
        self.assertIn("from_port   = 80", self.main_tf)
        self.assertIn("from_port   = 443", self.main_tf)
        self.assertIn("security_groups    = [aws_security_group.alb_sg.id]", self.main_tf)


if __name__ == "__main__":
    unittest.main()
