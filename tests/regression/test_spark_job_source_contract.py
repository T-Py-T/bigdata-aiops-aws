import ast
import unittest
from pathlib import Path

from tests.regression.support import REPOSITORY_ROOT


def _function_names(module: ast.Module) -> set[str]:
    return {
        node.name
        for node in module.body
        if isinstance(node, ast.FunctionDef)
    }


class SparkJobSourceContractTests(unittest.TestCase):
    def test_batch_processor_reads_parquet_and_filters_nulls(self):
        source_path = (
            REPOSITORY_ROOT / "services/spark_batch_processor/src/batch_processor.py"
        )
        tree = ast.parse(source_path.read_text(), filename=str(source_path))
        self.assertEqual(_function_names(tree), {"main"})
        source = source_path.read_text()
        self.assertIn('appName("SparkBatchProcessor")', source)
        self.assertIn("s3a://{{ S3_BUCKET }}", source)
        self.assertIn('filter("column IS NOT NULL")', source)
        self.assertIn("spark.stop()", source)

    def test_realtime_processor_uses_structured_streaming_console_sink(self):
        source_path = (
            REPOSITORY_ROOT / "services/realtime_processor/src/realtime_processor.py"
        )
        tree = ast.parse(source_path.read_text(), filename=str(source_path))
        self.assertEqual(_function_names(tree), {"main"})
        source = source_path.read_text()
        self.assertIn('appName("RealtimeProcessor")', source)
        self.assertIn("readStream", source)
        self.assertIn('format("console")', source)
        self.assertIn("awaitTermination()", source)


if __name__ == "__main__":
    unittest.main()
