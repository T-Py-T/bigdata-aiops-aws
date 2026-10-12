import unittest
from unittest.mock import MagicMock, patch

from tests.service_import_support import load_kafka_ingest_module


class KafkaIngestServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module, self.app = load_kafka_ingest_module()

    def test_health_endpoint_returns_ok_status(self) -> None:
        handler = self.app.routes[("GET", "/health")]
        self.assertEqual(handler(), {"status": "ok"})

    def test_ingest_sends_payload_to_ingest_topic(self) -> None:
        producer = MagicMock()
        with patch.object(self.module, "create_producer", return_value=producer):
            handler = self.app.routes[("POST", "/ingest")]
            payload = {"event": "purchase", "amount": 42}
            response = handler(payload)

        producer.send.assert_called_once_with("ingest_topic", payload)
        producer.flush.assert_called_once_with()
        producer.close.assert_called_once_with()
        self.assertEqual(response, {"message": "Data ingested"})

    def test_create_producer_targets_scaffold_kafka_broker_placeholder(self) -> None:
        sentinel = MagicMock()
        with patch.object(self.module, "KafkaProducer", return_value=sentinel) as kafka_producer:
            producer = self.module.create_producer()

        self.assertIs(producer, sentinel)
        _, kwargs = kafka_producer.call_args
        self.assertEqual(kwargs["bootstrap_servers"], ["{{ KAFKA_BROKER }}"])
        serialized = kwargs["value_serializer"]({"key": "value"})
        self.assertEqual(serialized, b'{"key": "value"}')


if __name__ == "__main__":
    unittest.main()
