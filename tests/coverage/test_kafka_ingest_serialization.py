import json
import unittest
from unittest.mock import MagicMock, patch

from tests.coverage.support import RouteRecordingApp, load_module


class KafkaIngestSerializationTests(unittest.TestCase):
    def _load(self):
        app = RouteRecordingApp()
        fastapi = MagicMock()
        fastapi.FastAPI.return_value = app
        kafka = MagicMock()
        module = load_module(
            "kafka_ingest_coverage",
            "services/kafka_ingest/src/ingest.py",
            stubs={"fastapi": fastapi, "kafka": kafka},
        )
        return module, app, kafka

    def test_health_handler_returns_ok(self) -> None:
        _, app, _ = self._load()
        self.assertEqual(app.routes[("GET", "/health")](), {"status": "ok"})

    def test_value_serializer_emits_json_bytes(self) -> None:
        module, _, kafka = self._load()
        producer = MagicMock()
        kafka.KafkaProducer.return_value = producer

        module.create_producer()
        _, kwargs = kafka.KafkaProducer.call_args
        payload = {"sample": "data"}
        self.assertEqual(
            kwargs["value_serializer"](payload),
            json.dumps(payload).encode(),
        )

    def test_ingest_closes_producer_after_flush(self) -> None:
        module, app, _ = self._load()
        producer = MagicMock()
        with patch.object(module, "create_producer", return_value=producer):
            response = app.routes[("POST", "/ingest")]({"event": "test"})

        producer.send.assert_called_once_with("ingest_topic", {"event": "test"})
        producer.flush.assert_called_once_with()
        producer.close.assert_called_once_with()
        self.assertEqual(response, {"message": "Data ingested"})


if __name__ == "__main__":
    unittest.main()
