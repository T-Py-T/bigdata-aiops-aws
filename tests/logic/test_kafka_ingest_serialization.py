import json
import unittest
from unittest.mock import MagicMock, patch

from .support import import_service_module


class KafkaIngestSerializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ingest = import_service_module("kafka_ingest", "ingest")

    def test_health_check_is_ok_payload(self):
        self.assertEqual(self.ingest.health_check(), {"status": "ok"})

    def test_create_producer_value_serializer_encodes_json_utf8(self):
        captured = {}

        def fake_producer(**kwargs):
            captured["serializer"] = kwargs["value_serializer"]
            return MagicMock()

        with patch.object(self.ingest, "KafkaProducer", fake_producer):
            self.ingest.create_producer()

        payload = {"event": "ingest", "count": 3}
        self.assertEqual(captured["serializer"](payload), json.dumps(payload).encode())

    def test_create_producer_targets_ingest_topic_broker_placeholder(self):
        captured = {}

        def fake_producer(**kwargs):
            captured.update(kwargs)
            return MagicMock()

        with patch.object(self.ingest, "KafkaProducer", fake_producer):
            self.ingest.create_producer()

        self.assertEqual(captured["bootstrap_servers"], ["{{ KAFKA_BROKER }}"])


if __name__ == "__main__":
    unittest.main()
