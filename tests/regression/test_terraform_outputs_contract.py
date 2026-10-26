import re
import unittest

from tests.regression.support import read_repo_file


class TerraformOutputsContractTests(unittest.TestCase):
    def test_outputs_surface_network_and_cluster_endpoints(self):
        outputs_tf = read_repo_file("infra/terraform/outputs.tf")
        declared = re.findall(r'^output\s+"([^"]+)"', outputs_tf, flags=re.MULTILINE)
        self.assertEqual(
            declared,
            [
                "vpc_id",
                "public_subnets",
                "private_subnets",
                "eks_cluster_name",
                "eks_cluster_endpoint",
                "alb_dns_name",
            ],
        )

    def test_output_values_reference_expected_modules(self):
        outputs_tf = read_repo_file("infra/terraform/outputs.tf")
        self.assertIn("module.vpc.vpc_id", outputs_tf)
        self.assertIn("module.vpc.public_subnets", outputs_tf)
        self.assertIn("module.vpc.private_subnets", outputs_tf)
        self.assertIn("module.eks.cluster_name", outputs_tf)
        self.assertIn("module.eks.cluster_endpoint", outputs_tf)
        self.assertIn("aws_lb.alb.dns_name", outputs_tf)


if __name__ == "__main__":
    unittest.main()
