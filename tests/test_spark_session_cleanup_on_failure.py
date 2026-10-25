"""Regression: Spark entrypoints must stop the session when processing fails."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _pyspark_stub() -> tuple[ModuleType, ModuleType, MagicMock]:
    pyspark = types.ModuleType("pyspark")
    pyspark_sql = types.ModuleType("pyspark.sql")
    spark = MagicMock()
    builder = MagicMock()
    builder.appName.return_value = builder
    builder.getOrCreate.return_value = spark
    pyspark_sql.SparkSession = MagicMock(builder=builder)
    pyspark.sql = pyspark_sql
    return pyspark, pyspark_sql, spark


def _load_spark_module(relative_path: str, module_name: str) -> tuple[ModuleType, MagicMock]:
    pyspark, pyspark_sql, spark = _pyspark_stub()
    for name in ("pyspark", "pyspark.sql", module_name):
        sys.modules.pop(name, None)

    source_path = REPOSITORY_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, source_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {source_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["pyspark"] = pyspark
    sys.modules["pyspark.sql"] = pyspark_sql
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module, spark


class SparkSessionCleanupOnFailureTests(unittest.TestCase):
    def test_batch_processor_stops_spark_when_parquet_read_fails(self) -> None:
        module, spark = _load_spark_module(
            "services/spark_batch_processor/src/batch_processor.py",
            "batch_processor_cleanup_test",
        )
        spark.read.parquet.side_effect = OSError("s3 unavailable")

        with self.assertRaises(OSError):
            module.main()

        spark.stop.assert_called_once()

    def test_realtime_processor_stops_spark_when_stream_setup_fails(self) -> None:
        module, spark = _load_spark_module(
            "services/realtime_processor/src/realtime_processor.py",
            "realtime_processor_cleanup_test",
        )
        spark.readStream.format.return_value.load.side_effect = OSError("s3 unavailable")

        with self.assertRaises(OSError):
            module.main()

        spark.stop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
