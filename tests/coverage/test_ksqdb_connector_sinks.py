import unittest
from unittest.mock import MagicMock, patch

from tests.coverage.support import load_module


class KsqdbConnectorSinkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module(
            "ksqdb_connector_coverage",
            "services/ksqdb_connector/src/connector.py",
            stubs={"requests": MagicMock()},
        )

    def test_push_to_pinot_logs_without_network_call(self) -> None:
        with patch.object(self.module, "logging") as logging:
            self.module.push_to_pinot({"id": 1})
        logging.info.assert_called_once()
        self.module.requests.post.assert_not_called()

    def test_push_to_elastic_logs_without_network_call(self) -> None:
        with patch.object(self.module, "logging") as logging:
            self.module.push_to_elastic({"id": 1})
        logging.info.assert_called_once()
        self.module.requests.post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
