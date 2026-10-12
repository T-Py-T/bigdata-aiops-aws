import re
import unittest
from pathlib import Path

from .support import REPOSITORY_ROOT

K8S_BASE = REPOSITORY_ROOT / "infra" / "k8s" / "base"


class K8sBaseInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kustomization = (K8S_BASE / "kustomization.yaml").read_text()

    def test_kustomization_lists_only_existing_resource_files(self):
        listed = re.findall(r"^\s*-\s+(\S+\.yaml)\s*$", self.kustomization, re.MULTILINE)
        self.assertTrue(listed)
        for resource in listed:
            self.assertTrue((K8S_BASE / resource).is_file(), resource)

    def test_image_placeholders_cover_ten_services(self):
        image_names = re.findall(r"name: \{\{ ([A-Z0-9_]+) \}\}", self.kustomization)
        self.assertEqual(len(image_names), 10)
        self.assertEqual(len(set(image_names)), 10)

    def test_each_image_uses_latest_tag_in_base(self):
        for block in re.findall(
            r"- name: \{\{ [A-Z0-9_]+ \}\}.*?(?=\n  - name:|\Z)",
            self.kustomization,
            re.DOTALL,
        ):
            self.assertIn('newTag: "latest"', block)


if __name__ == "__main__":
    unittest.main()
