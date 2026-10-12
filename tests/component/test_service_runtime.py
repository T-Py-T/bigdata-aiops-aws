import json
import unittest
from unittest.mock import MagicMock, patch

from component.support import import_service_module


class KafkaIngestRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ingest = import_service_module("kafka_ingest", "ingest")

    def test_health_check_returns_ok(self):
        self.assertEqual(self.ingest.health_check(), {"status": "ok"})

    def test_create_producer_serializes_json(self):
        with patch.object(self.ingest, "KafkaProducer") as mock_producer:
            self.ingest.create_producer()
        _, kwargs = mock_producer.call_args
        payload = {"n": 1}
        self.assertEqual(kwargs["value_serializer"](payload), json.dumps(payload).encode())

    def test_ingest_data_publishes_and_closes_producer(self):
        producer = MagicMock()
        body = {"event": "click"}

        with patch.object(self.ingest, "create_producer", return_value=producer):
            result = self.ingest.ingest_data(body)

        self.assertEqual(result, {"message": "Data ingested"})
        producer.send.assert_called_once_with("ingest_topic", body)
        producer.flush.assert_called_once()
        producer.close.assert_called_once()

    def test_ingest_data_closes_producer_on_failure(self):
        producer = MagicMock()
        producer.send.side_effect = OSError("broker down")

        with patch.object(self.ingest, "create_producer", return_value=producer):
            with self.assertRaises(OSError):
                self.ingest.ingest_data({"bad": True})

        producer.close.assert_called_once()

    def test_fastapi_app_registers_health_and_ingest_routes(self):
        route_paths = {route.path for route in self.ingest.app.routes}
        self.assertIn("/health", route_paths)
        self.assertIn("/ingest", route_paths)


class StreamProcessorRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.processor = import_service_module("python_stream_processor", "processor")

    def test_value_deserializer_parses_utf8_json(self):
        with patch.object(self.processor, "KafkaConsumer") as mock_consumer:
            self.processor.create_consumer()
        _, kwargs = mock_consumer.call_args
        raw = json.dumps({"k": "v"}).encode("utf-8")
        self.assertEqual(kwargs["value_deserializer"](raw), {"k": "v"})

    def test_process_message_logs_payload(self):
        with self.assertLogs(level="INFO") as logs:
            self.processor.process_message({"hello": "world"})
        self.assertIn("Processing message: {'hello': 'world'}", logs.output[0])


class KsqdbConnectorRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connector = import_service_module("ksqdb_connector", "connector")

    def test_push_to_pinot_logs(self):
        with self.assertLogs(level="INFO") as logs:
            self.connector.push_to_pinot({"table": "events"})
        self.assertIn("Pushing data to Pinot:", logs.output[0])

    def test_push_to_elastic_logs(self):
        with self.assertLogs(level="INFO") as logs:
            self.connector.push_to_elastic({"index": "logs"})
        self.assertIn("Pushing data to Elastic:", logs.output[0])


if __name__ == "__main__":
    unittest.main()
