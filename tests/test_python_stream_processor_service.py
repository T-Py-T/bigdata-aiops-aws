import json
import logging
import unittest
from unittest.mock import MagicMock, patch

from tests.service_import_support import load_stream_processor_module


class PythonStreamProcessorServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_stream_processor_module()

    def test_create_consumer_subscribes_to_ingest_topic(self) -> None:
        consumer = MagicMock()
        with patch.object(self.module, "KafkaConsumer", return_value=consumer) as kafka_consumer:
            created = self.module.create_consumer()

        self.assertIs(created, consumer)
        kafka_consumer.assert_called_once_with(
            "ingest_topic",
            bootstrap_servers=["{{ KAFKA_BROKER }}"],
            value_deserializer=kafka_consumer.call_args.kwargs["value_deserializer"],
        )
        deserializer = kafka_consumer.call_args.kwargs["value_deserializer"]
        payload = {"stream": "event"}
        self.assertEqual(deserializer(json.dumps(payload).encode("utf-8")), payload)

    def test_process_message_emits_info_log(self) -> None:
        with self.assertLogs("root", level="INFO") as captured:
            self.module.process_message({"id": 7})

        self.assertIn("Processing message: {'id': 7}", captured.output[0])


if __name__ == "__main__":
    unittest.main()
