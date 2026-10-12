import re
import unittest

from infra.support import REPOSITORY_ROOT

GENERATOR = REPOSITORY_ROOT / "create_project.sh"


class GeneratorSparkScaffoldTests(unittest.TestCase):
    def test_generator_declares_spark_service_directories(self):
        content = GENERATOR.read_text()
        for path in (
            "services/spark_batch_processor/src",
            "services/realtime_processor/src",
        ):
            self.assertIn(f'"{path}"', content)

    def test_generator_emits_batch_and_streaming_processor_sources(self):
        content = GENERATOR.read_text()
        self.assertIn('appName("SparkBatchProcessor")', content)
        self.assertIn('appName("RealtimeProcessor")', content)
        self.assertIn('filter("column IS NOT NULL")', content)
        self.assertIn("readStream", content)

    def test_generator_pins_spark_parent_images(self):
        content = GENERATOR.read_text()
        spark_from_lines = re.findall(
            r"^FROM spark:[^\s]+@sha256:[0-9a-f]{64}$",
            content,
            re.MULTILINE,
        )
        self.assertGreaterEqual(len(spark_from_lines), 2)


if __name__ == "__main__":
    unittest.main()
