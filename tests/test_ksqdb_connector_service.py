import logging
import unittest

from tests.service_import_support import load_ksqdb_connector_module


class KsqdbConnectorServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_ksqdb_connector_module()

    def test_push_to_pinot_logs_payload(self) -> None:
        payload = {"metric": "throughput", "value": 1200}
        with self.assertLogs("root", level="INFO") as captured:
            self.module.push_to_pinot(payload)

        self.assertIn("Pushing data to Pinot", captured.output[0])
        self.assertIn(str(payload), captured.output[0])

    def test_push_to_elastic_logs_payload(self) -> None:
        payload = {"index": "events", "count": 3}
        with self.assertLogs("root", level="INFO") as captured:
            self.module.push_to_elastic(payload)

        self.assertIn("Pushing data to Elastic", captured.output[0])
        self.assertIn(str(payload), captured.output[0])


if __name__ == "__main__":
    unittest.main()
