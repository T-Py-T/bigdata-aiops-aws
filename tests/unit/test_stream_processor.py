import json
import unittest
from unittest import mock

from support import import_service_module


class StreamProcessorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.processor = import_service_module("python_stream_processor", "processor")

    def test_decode_kafka_value_parses_json_bytes(self):
        payload = {"metric": 42, "ok": True}
        raw = json.dumps(payload).encode("utf-8")
        self.assertEqual(self.processor.decode_kafka_value(raw), payload)

    def test_decode_kafka_value_rejects_invalid_json(self):
        with self.assertRaises(json.JSONDecodeError):
            self.processor.decode_kafka_value(b"not-json")

    def test_process_message_logs_payload(self):
        with self.assertLogs(level="INFO") as logs:
            self.processor.process_message({"hello": "world"})
        self.assertIn("Processing message: {'hello': 'world'}", logs.output[0])

    def test_create_consumer_uses_decode_kafka_value(self):
        with mock.patch.object(self.processor, "KafkaConsumer") as mock_consumer:
            self.processor.create_consumer()
        _, kwargs = mock_consumer.call_args
        self.assertIs(kwargs["value_deserializer"], self.processor.decode_kafka_value)


if __name__ == "__main__":
    unittest.main()
