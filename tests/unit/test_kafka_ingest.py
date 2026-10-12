import unittest
from unittest.mock import MagicMock, patch

from support import import_service_module


class KafkaIngestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ingest = import_service_module("kafka_ingest", "ingest")

    def test_health_check_returns_ok(self):
        self.assertEqual(self.ingest.health_check(), {"status": "ok"})

    def test_ingest_data_sends_to_kafka_and_closes_producer(self):
        producer = MagicMock()
        payload = {"event": "sample"}

        with patch.object(self.ingest, "create_producer", return_value=producer):
            result = self.ingest.ingest_data(payload)

        self.assertEqual(result, {"message": "Data ingested"})
        producer.send.assert_called_once_with("ingest_topic", payload)
        producer.flush.assert_called_once()
        producer.close.assert_called_once()

    def test_ingest_data_closes_producer_when_send_fails(self):
        producer = MagicMock()
        producer.send.side_effect = RuntimeError("broker unavailable")

        with patch.object(self.ingest, "create_producer", return_value=producer):
            with self.assertRaises(RuntimeError):
                self.ingest.ingest_data({"broken": True})

        producer.close.assert_called_once()

    def test_fastapi_ingest_endpoint_accepts_json_body(self):
        from fastapi.testclient import TestClient

        producer = MagicMock()
        with patch.object(self.ingest, "create_producer", return_value=producer):
            response = TestClient(self.ingest.app).post("/ingest", json={"via": "http"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Data ingested"})
        producer.send.assert_called_once_with("ingest_topic", {"via": "http"})


if __name__ == "__main__":
    unittest.main()
