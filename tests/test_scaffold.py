import ast
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
GENERATED_DEPENDENCY_FILES = (
    "infra/airflow/Dockerfile",
    "infra/airflow/dags/pipeline_dag.py",
    "infra/k8s/base/visualization_superset-deployment.yaml",
    "services/data_catalog/Dockerfile",
    "services/kafka_ingest/Dockerfile",
    "services/kafka_ingest/requirements.txt",
    "services/kafka_ingest/src/ingest.py",
    "services/ksqdb_connector/Dockerfile",
    "services/ksqdb_connector/requirements.txt",
    "services/ksqdb_connector/src/connector.py",
    "services/python_stream_processor/Dockerfile",
    "services/python_stream_processor/requirements.txt",
    "services/python_stream_processor/src/processor.py",
    "services/realtime_processor/Dockerfile",
    "services/realtime_processor/src/realtime_processor.py",
    "services/serving_trino/Dockerfile",
    "services/serving_trino/config/config.properties",
    "services/spark_batch_processor/Dockerfile",
    "services/spark_batch_processor/src/batch_processor.py",
    "services/visualization_metabase/Dockerfile",
    "services/visualization_superset/Dockerfile",
)


class ScaffoldTests(unittest.TestCase):
    def test_generator_matches_checked_in_dependencies(self):
        with tempfile.TemporaryDirectory() as generated_root:
            result = subprocess.run(
                ["bash", str(REPOSITORY_ROOT / "create_project.sh")],
                cwd=generated_root,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.stderr, "")
            for relative_path in GENERATED_DEPENDENCY_FILES:
                expected = (REPOSITORY_ROOT / relative_path).read_text()
                generated = (Path(generated_root) / relative_path).read_text()
                self.assertEqual(generated, expected, relative_path)

    def test_parent_images_are_immutable(self):
        for dockerfile in REPOSITORY_ROOT.glob("**/Dockerfile"):
            first_line = dockerfile.read_text().splitlines()[0]
            self.assertRegex(
                first_line,
                r"^FROM [^\s]+@sha256:[0-9a-f]{64}$",
                str(dockerfile.relative_to(REPOSITORY_ROOT)),
            )

    def test_python_sources_parse(self):
        source_roots = (REPOSITORY_ROOT / "services", REPOSITORY_ROOT / "infra")
        for source_root in source_roots:
            for source_file in source_root.rglob("*.py"):
                ast.parse(source_file.read_text(), filename=str(source_file))

    def test_pr_checks_include_security_audits(self):
        workflow = (REPOSITORY_ROOT / ".github" / "workflows" / "pr-checks.yml").read_text()
        self.assertIn("pip==26.2.1", workflow)
        self.assertIn("pip-audit", workflow)
        self.assertIn("scripts/security_audit.sh", workflow)

    def test_terraform_aws_provider_is_pinned(self):
        main_tf = (REPOSITORY_ROOT / "infra" / "terraform" / "main.tf").read_text()
        self.assertIn('version = "6.68.0"', main_tf)

    def test_python_service_base_images_are_current(self):
        expected_digest = (
            "python:3.14.7-slim-trixie@"
            "sha256:51dafde81dbdb6ebde285137a295cf18a47ca95234fe388a343719cb97305b3d"
        )
        for relative_path in (
            "services/kafka_ingest/Dockerfile",
            "services/ksqdb_connector/Dockerfile",
            "services/python_stream_processor/Dockerfile",
        ):
            first_line = (REPOSITORY_ROOT / relative_path).read_text().splitlines()[0]
            self.assertEqual(first_line, f"FROM {expected_digest}", relative_path)

    def test_workflows_are_pull_request_only(self):
        workflows = tuple((REPOSITORY_ROOT / ".github" / "workflows").glob("*"))
        self.assertTrue(workflows)
        forbidden_triggers = re.compile(
            r"^\s{0,2}(push|schedule|workflow_dispatch|repository_dispatch|workflow_run):",
            re.MULTILINE,
        )
        for workflow in workflows:
            content = workflow.read_text()
            self.assertIn("\n  pull_request:\n", content)
            self.assertIsNone(forbidden_triggers.search(content), workflow.name)


if __name__ == "__main__":
    unittest.main()
