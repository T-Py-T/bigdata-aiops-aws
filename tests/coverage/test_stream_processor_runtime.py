import json
import unittest
from unittest.mock import MagicMock

from tests.coverage.support import load_module


class StreamProcessorRuntimeTests(unittest.TestCase):
    def test_create_consumer_targets_ingest_topic_and_broker_placeholder(self) -> None:
        kafka = MagicMock()
        consumer = MagicMock()
        kafka.KafkaConsumer.return_value = consumer

        module = load_module(
            "stream_processor_coverage",
            "services/python_stream_processor/src/processor.py",
            stubs={"kafka": kafka},
        )

        created = module.create_consumer()

        self.assertIs(created, consumer)
        kafka.KafkaConsumer.assert_called_once()
        _, kwargs = kafka.KafkaConsumer.call_args
        self.assertEqual(kwargs["bootstrap_servers"], ["{{ KAFKA_BROKER }}"])
        serialized = json.dumps({"ok": True}).encode("utf-8")
        self.assertEqual(kwargs["value_deserializer"](serialized), {"ok": True})

    def test_process_message_accepts_decoded_payload(self) -> None:
        module = load_module(
            "stream_processor_coverage_message",
            "services/python_stream_processor/src/processor.py",
            stubs={"kafka": MagicMock()},
        )
        module.process_message({"event": "click"})


if __name__ == "__main__":
    unittest.main()
