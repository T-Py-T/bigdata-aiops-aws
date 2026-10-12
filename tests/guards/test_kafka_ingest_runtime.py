import json
import sys
import types
import unittest
from types import ModuleType
from unittest.mock import MagicMock

from tests.guards.support import load_module_from_path


def _fastapi_stub() -> ModuleType:
    fastapi = types.ModuleType("fastapi")

    class FastAPI:
        def __init__(self):
            self._routes = {}

        def get(self, path):
            def decorator(func):
                self._routes[("GET", path)] = func
                return func

            return decorator

        def post(self, path):
            def decorator(func):
                self._routes[("POST", path)] = func
                return func

            return decorator

    fastapi.FastAPI = FastAPI
    return fastapi


def _kafka_stub() -> ModuleType:
    kafka = types.ModuleType("kafka")
    kafka.KafkaProducer = MagicMock()
    return kafka


class KafkaIngestRuntimeTests(unittest.TestCase):
    def setUp(self):
        self._saved_modules = {
            name: sys.modules.get(name) for name in ("fastapi", "kafka", "ingest_guard")
        }

    def tearDown(self):
        for name, module in self._saved_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module

    def _load_ingest(self):
        return load_module_from_path(
            "services/kafka_ingest/src/ingest.py",
            "ingest_guard",
            {
                "fastapi": _fastapi_stub(),
                "kafka": _kafka_stub(),
            },
        )

    def test_health_endpoint_returns_ok_status(self):
        ingest = self._load_ingest()
        response = ingest.app._routes[("GET", "/health")]()
        self.assertEqual(response, {"status": "ok"})

    def test_ingest_sends_payload_and_closes_producer(self):
        ingest = self._load_ingest()
        producer = MagicMock()
        ingest.create_producer = MagicMock(return_value=producer)

        payload = {"event": "unit-test"}
        response = ingest.app._routes[("POST", "/ingest")](payload)

        producer.send.assert_called_once_with("ingest_topic", payload)
        producer.flush.assert_called_once()
        producer.close.assert_called_once()
        self.assertEqual(response, {"message": "Data ingested"})

    def test_create_producer_serializes_json_payloads(self):
        ingest = self._load_ingest()
        ingest.create_producer()
        serializer = ingest.KafkaProducer.call_args.kwargs["value_serializer"]
        self.assertEqual(serializer({"a": 1}), json.dumps({"a": 1}).encode())


if __name__ == "__main__":
    unittest.main()
