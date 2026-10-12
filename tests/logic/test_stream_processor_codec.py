import json
import unittest
from unittest import mock

from .support import import_service_module


class StreamProcessorCodecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.processor = import_service_module("python_stream_processor", "processor")

    def test_consumer_value_deserializer_parses_json_bytes(self):
        captured = {}

        def fake_consumer(*_args, **kwargs):
            captured["deserializer"] = kwargs["value_deserializer"]
            return mock.MagicMock()

        with mock.patch.object(self.processor, "KafkaConsumer", fake_consumer):
            self.processor.create_consumer()

        payload = {"metric": 99, "ok": True}
        raw = json.dumps(payload).encode("utf-8")
        self.assertEqual(captured["deserializer"](raw), payload)

    def test_consumer_value_deserializer_rejects_invalid_json(self):
        captured = {}

        def fake_consumer(*_args, **kwargs):
            captured["deserializer"] = kwargs["value_deserializer"]
            return mock.MagicMock()

        with mock.patch.object(self.processor, "KafkaConsumer", fake_consumer):
            self.processor.create_consumer()

        with self.assertRaises(json.JSONDecodeError):
            captured["deserializer"](b"not-json")

    def test_process_message_logs_payload(self):
        with self.assertLogs(level="INFO") as logs:
            self.processor.process_message({"hello": "stream"})
        self.assertIn("Processing message: {'hello': 'stream'}", logs.output[0])


if __name__ == "__main__":
    unittest.main()
