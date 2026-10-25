import ast
import unittest
from pathlib import Path

from tests.coverage.support import REPOSITORY_ROOT


def _function_calls(tree: ast.AST) -> list[ast.Call]:
    return [node for node in ast.walk(tree) if isinstance(node, ast.Call)]


class SparkProcessorAstTests(unittest.TestCase):
    def test_batch_processor_filters_nullable_column_and_stops_spark(self) -> None:
        path = REPOSITORY_ROOT / "services/spark_batch_processor/src/batch_processor.py"
        tree = ast.parse(path.read_text(), filename=str(path))
        source = path.read_text()
        self.assertIn('df.filter("column IS NOT NULL")', source)
        self.assertIn("spark.stop()", source)
        self.assertIn('s3a://{{ S3_BUCKET }}', source)
        attr_calls = {
            (call.func.attr if isinstance(call.func, ast.Attribute) else None)
            for call in _function_calls(tree)
        }
        self.assertIn("parquet", attr_calls)
        self.assertIn("filter", attr_calls)
        self.assertIn("show", attr_calls)
        self.assertIn("stop", attr_calls)

    def test_realtime_processor_uses_parquet_console_stream(self) -> None:
        path = REPOSITORY_ROOT / "services/realtime_processor/src/realtime_processor.py"
        source = path.read_text()
        tree = ast.parse(source, filename=str(path))
        self.assertIn('format("parquet")', source)
        self.assertIn('format("console")', source)
        self.assertIn("awaitTermination()", source)
        self.assertIn('s3a://{{ S3_BUCKET }}', source)
        chained_attrs = []
        for call in _function_calls(tree):
            if isinstance(call.func, ast.Attribute):
                parts = []
                node = call.func
                while isinstance(node, ast.Attribute):
                    parts.append(node.attr)
                    node = node.value
                chained_attrs.append(".".join(reversed(parts)))
        self.assertIn("readStream.format", chained_attrs)
        self.assertIn("writeStream.format", chained_attrs)
        self.assertIn("awaitTermination", chained_attrs)


if __name__ == "__main__":
    unittest.main()
