import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _load_module(relative_path: str, module_name: str):
    path = REPOSITORY_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class KafkaBrokerEnvironmentTests(unittest.TestCase):
    def test_ingest_uses_kafka_broker_environment_variable(self):
        fastapi_stub = mock.MagicMock()
        fastapi_stub.FastAPI = mock.MagicMock(return_value=mock.MagicMock())
        with mock.patch.dict(
            sys.modules,
            {"kafka": mock.MagicMock(), "fastapi": fastapi_stub},
        ):
            ingest = _load_module(
                "services/kafka_ingest/src/ingest.py",
                "ingest_kafka_broker_env",
            )
            with mock.patch.dict(os.environ, {"KAFKA_BROKER": "broker.example:9092"}):
                self.assertEqual(
                    ingest.kafka_bootstrap_servers(),
                    ["broker.example:9092"],
                )
            with mock.patch.dict(os.environ, {}, clear=True):
                self.assertEqual(
                    ingest.kafka_bootstrap_servers(),
                    ["{{ KAFKA_BROKER }}"],
                )

    def test_stream_processor_uses_kafka_broker_environment_variable(self):
        with mock.patch.dict(sys.modules, {"kafka": mock.MagicMock()}):
            processor = _load_module(
                "services/python_stream_processor/src/processor.py",
                "processor_kafka_broker_env",
            )
            with mock.patch.dict(os.environ, {"KAFKA_BROKER": "kafka:9092"}):
                self.assertEqual(
                    processor.kafka_bootstrap_servers(),
                    ["kafka:9092"],
                )

    def test_stream_processor_deployment_declares_kafka_broker_env(self):
        deployment = (
            REPOSITORY_ROOT
            / "infra/k8s/base/python_stream_processor-deployment.yaml"
        ).read_text()
        self.assertIn("KAFKA_BROKER", deployment)


if __name__ == "__main__":
    unittest.main()
