"""Regression: Kafka clients must honor the KAFKA_BROKER env set by Kubernetes."""

from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _load_module(relative_path: str, module_name: str, stubs: dict[str, object]) -> ModuleType:
    for name, value in stubs.items():
        sys.modules[name] = value  # type: ignore[assignment]

    source_path = REPOSITORY_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, source_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {source_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class KafkaBootstrapFromEnvironmentTests(unittest.TestCase):
    def test_ingest_create_producer_uses_kafka_broker_environment_variable(self) -> None:
        kafka = MagicMock()
        sentinel = MagicMock()
        kafka.KafkaProducer.return_value = sentinel

        module = _load_module(
            "services/kafka_ingest/src/ingest.py",
            "kafka_ingest_env_test",
            {"kafka": kafka, "fastapi": MagicMock()},
        )

        with patch.dict(os.environ, {"KAFKA_BROKER": "kafka-broker.svc:9092"}, clear=False):
            producer = module.create_producer()

        self.assertIs(producer, sentinel)
        _, kwargs = kafka.KafkaProducer.call_args
        self.assertEqual(kwargs["bootstrap_servers"], ["kafka-broker.svc:9092"])

    def test_stream_processor_create_consumer_uses_kafka_broker_environment_variable(
        self,
    ) -> None:
        kafka = MagicMock()
        sentinel = MagicMock()
        kafka.KafkaConsumer.return_value = sentinel

        module = _load_module(
            "services/python_stream_processor/src/processor.py",
            "stream_processor_env_test",
            {"kafka": kafka},
        )

        with patch.dict(os.environ, {"KAFKA_BROKER": "kafka-broker.svc:9092"}, clear=False):
            consumer = module.create_consumer()

        self.assertIs(consumer, sentinel)
        _, kwargs = kafka.KafkaConsumer.call_args
        self.assertEqual(kwargs["bootstrap_servers"], ["kafka-broker.svc:9092"])


if __name__ == "__main__":
    unittest.main()
