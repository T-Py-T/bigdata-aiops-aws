import unittest

from .support import import_service_module


class KsqdbConnectorLoggingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connector = import_service_module("ksqdb_connector", "connector")

    def test_push_to_pinot_logs_payload(self):
        with self.assertLogs(level="INFO") as logs:
            self.connector.push_to_pinot({"table": "events"})
        self.assertIn("Pushing data to Pinot: {'table': 'events'}", logs.output[0])

    def test_push_to_elastic_logs_payload(self):
        with self.assertLogs(level="INFO") as logs:
            self.connector.push_to_elastic({"index": "logs"})
        self.assertIn("Pushing data to Elastic: {'index': 'logs'}", logs.output[0])


if __name__ == "__main__":
    unittest.main()
