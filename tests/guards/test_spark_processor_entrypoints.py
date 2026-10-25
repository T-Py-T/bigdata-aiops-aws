import sys
import types
import unittest
from types import ModuleType
from unittest.mock import MagicMock

from tests.guards.support import load_module_from_path


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


class SparkProcessorEntrypointTests(unittest.TestCase):
    def setUp(self):
        self._saved_modules = {
            name: sys.modules.get(name)
            for name in (
                "pyspark",
                "pyspark.sql",
                "batch_processor_guard",
                "realtime_processor_guard",
            )
        }

    def tearDown(self):
        for name, module in self._saved_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module

    def test_batch_processor_reads_filters_and_stops_spark(self):
        pyspark, pyspark_sql, spark = _pyspark_stub()
        frame = MagicMock()
        filtered = MagicMock()
        spark.read.parquet.return_value = frame
        frame.filter.return_value = filtered

        batch = load_module_from_path(
            "services/spark_batch_processor/src/batch_processor.py",
            "batch_processor_guard",
            {"pyspark": pyspark, "pyspark.sql": pyspark_sql},
        )
        batch.main()

        spark.read.parquet.assert_called_once_with("s3a://{{ S3_BUCKET }}")
        frame.filter.assert_called_once_with("column IS NOT NULL")
        filtered.show.assert_called_once()
        spark.stop.assert_called_once()

    def test_realtime_processor_starts_console_stream(self):
        pyspark, pyspark_sql, spark = _pyspark_stub()
        frame = MagicMock()
        writer = MagicMock()
        query = MagicMock()
        spark.readStream.format.return_value.load.return_value = frame
        frame.writeStream.format.return_value = writer
        writer.start.return_value = query

        realtime = load_module_from_path(
            "services/realtime_processor/src/realtime_processor.py",
            "realtime_processor_guard",
            {"pyspark": pyspark, "pyspark.sql": pyspark_sql},
        )
        realtime.main()

        spark.readStream.format.assert_called_once_with("parquet")
        spark.readStream.format.return_value.load.assert_called_once_with("s3a://{{ S3_BUCKET }}")
        frame.writeStream.format.assert_called_once_with("console")
        query.awaitTermination.assert_called_once()


if __name__ == "__main__":
    unittest.main()
