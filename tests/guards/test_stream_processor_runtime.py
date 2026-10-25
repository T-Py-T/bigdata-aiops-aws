import json
import sys
import types
import unittest
from types import ModuleType
from unittest.mock import MagicMock

from tests.guards.support import load_module_from_path


def _kafka_consumer_stub() -> ModuleType:
    kafka = types.ModuleType("kafka")
    kafka.KafkaConsumer = MagicMock()
    return kafka


class StreamProcessorRuntimeTests(unittest.TestCase):
    def setUp(self):
        self._saved_modules = {
            name: sys.modules.get(name) for name in ("kafka", "processor_guard")
        }

    def tearDown(self):
        for name, module in self._saved_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module

    def _load_processor(self):
        return load_module_from_path(
            "services/python_stream_processor/src/processor.py",
            "processor_guard",
            {"kafka": _kafka_consumer_stub()},
        )

    def test_consumer_deserializer_parses_utf8_json(self):
        processor = self._load_processor()
        processor.create_consumer()
        deserializer = processor.KafkaConsumer.call_args.kwargs["value_deserializer"]
        message = json.dumps({"id": 7}).encode("utf-8")
        self.assertEqual(deserializer(message), {"id": 7})

    def test_process_message_accepts_mapping_payload(self):
        processor = self._load_processor()
        with self.assertLogs("root", level="INFO") as captured:
            processor.process_message({"id": 7})
        self.assertIn("Processing message: {'id': 7}", captured.output[0])


if __name__ == "__main__":
    unittest.main()
