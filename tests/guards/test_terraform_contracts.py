import unittest

from tests.guards.support import (
    read_repo_text,
    terraform_output_names,
    terraform_variable_defaults,
)


class TerraformContractTests(unittest.TestCase):
    def test_outputs_cover_network_compute_and_ingress(self):
        outputs = terraform_output_names(read_repo_text("infra", "terraform", "outputs.tf"))
        self.assertEqual(
            outputs,
            {
                "vpc_id",
                "public_subnets",
                "private_subnets",
                "eks_cluster_name",
                "eks_cluster_endpoint",
                "alb_dns_name",
            },
        )

    def test_eks_and_node_group_defaults_are_pinned(self):
        defaults = terraform_variable_defaults(read_repo_text("infra", "terraform", "variables.tf"))
        self.assertEqual(defaults["cluster_version"], '"1.35"')
        self.assertEqual(defaults["instance_type"], '"t3.medium"')
        self.assertEqual(defaults["desired_capacity"], "2")
        self.assertEqual(defaults["min_capacity"], "1")
        self.assertEqual(defaults["max_capacity"], "3")

    def test_required_inputs_have_no_default(self):
        defaults = terraform_variable_defaults(read_repo_text("infra", "terraform", "variables.tf"))
        for required in (
            "region",
            "vpc_name",
            "vpc_cidr",
            "azs",
            "public_subnets",
            "private_subnets",
            "cluster_name",
            "environment",
            "project",
        ):
            self.assertIsNone(defaults[required], required)


if __name__ == "__main__":
    unittest.main()
