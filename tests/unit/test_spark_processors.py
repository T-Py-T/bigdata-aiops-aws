import ast
import unittest
from pathlib import Path

from support import REPOSITORY_ROOT


class SparkProcessorSourceTests(unittest.TestCase):
    def test_batch_processor_filters_and_stops_spark(self):
        source = (
            REPOSITORY_ROOT
            / "services"
            / "spark_batch_processor"
            / "src"
            / "batch_processor.py"
        ).read_text()
        tree = ast.parse(source)
        main_fn = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "main"
        )
        calls = {
            node.func.attr
            for node in ast.walk(main_fn)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "spark"
        }
        self.assertIn("stop", calls)
        self.assertIn('s3a://{{ S3_BUCKET }}', source)
        self.assertIn("column IS NOT NULL", source)

    def test_realtime_processor_uses_structured_streaming(self):
        source = (
            REPOSITORY_ROOT
            / "services"
            / "realtime_processor"
            / "src"
            / "realtime_processor.py"
        ).read_text()
        self.assertIn("readStream", source)
        self.assertIn("writeStream", source)
        self.assertIn('s3a://{{ S3_BUCKET }}', source)


if __name__ == "__main__":
    unittest.main()
