import ast
import unittest
from pathlib import Path

from infra.support import REPOSITORY_ROOT

SPARK_SERVICES = (
    ("spark_batch_processor", "batch_processor.py", "SparkBatchProcessor"),
    ("realtime_processor", "realtime_processor.py", "RealtimeProcessor"),
)


def _load_main_function(source_path: Path) -> ast.FunctionDef:
    tree = ast.parse(source_path.read_text(), filename=str(source_path))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            return node
    raise AssertionError(f"{source_path} must define main()")


def _call_names(function: ast.FunctionDef) -> list[str]:
    names: list[str] = []
    for node in ast.walk(function):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                names.append(node.func.attr)
            elif isinstance(node.func, ast.Name):
                names.append(node.func.id)
    return names


class SparkDataJobTests(unittest.TestCase):
    def test_batch_job_reads_filters_and_stops_spark(self):
        source = (
            REPOSITORY_ROOT
            / "services"
            / "spark_batch_processor"
            / "src"
            / "batch_processor.py"
        )
        text = source.read_text()
        self.assertIn('appName("SparkBatchProcessor")', text)
        self.assertIn("s3a://{{ S3_BUCKET }}", text)
        self.assertIn('filter("column IS NOT NULL")', text)

        calls = _call_names(_load_main_function(source))
        self.assertIn("parquet", calls)
        self.assertIn("filter", calls)
        self.assertIn("show", calls)
        self.assertIn("stop", calls)

    def test_realtime_job_uses_structured_streaming_console_sink(self):
        source = (
            REPOSITORY_ROOT
            / "services"
            / "realtime_processor"
            / "src"
            / "realtime_processor.py"
        )
        text = source.read_text()
        self.assertIn('appName("RealtimeProcessor")', text)
        self.assertIn("readStream", text)
        self.assertIn('format("parquet")', text)
        self.assertIn('format("console")', text)

        calls = _call_names(_load_main_function(source))
        self.assertIn("load", calls)
        self.assertIn("start", calls)
        self.assertIn("awaitTermination", calls)
        self.assertGreaterEqual(calls.count("format"), 2)

    def test_spark_dockerfiles_submit_expected_entrypoints(self):
        for service_name, script_name, _ in SPARK_SERVICES:
            dockerfile = REPOSITORY_ROOT / "services" / service_name / "Dockerfile"
            content = dockerfile.read_text()
            self.assertIn("spark-submit", content, service_name)
            self.assertIn(script_name, content, service_name)

    def test_kubernetes_deployments_run_matching_scripts(self):
        deployment_names = {
            "spark_batch_processor": "batch_processor.py",
            "realtime_processor": "realtime_processor.py",
        }
        for service_name, script_name in deployment_names.items():
            manifest = (
                REPOSITORY_ROOT
                / "infra"
                / "k8s"
                / "base"
                / f"{service_name}-deployment.yaml"
            )
            content = manifest.read_text()
            self.assertIn(script_name, content, service_name)


if __name__ == "__main__":
    unittest.main()
