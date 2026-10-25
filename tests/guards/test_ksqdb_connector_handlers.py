import unittest

from tests.guards.support import load_module_from_path


class KsqdbConnectorHandlerTests(unittest.TestCase):
    def test_push_helpers_log_without_calling_remote_services(self):
        connector = load_module_from_path(
            "services/ksqdb_connector/src/connector.py",
            "connector_guard",
        )
        payload = {"metric": "latency", "value": 42}

        with self.assertLogs("root", level="INFO") as captured:
            connector.push_to_pinot(payload)
            connector.push_to_elastic(payload)

        joined = "\n".join(captured.output)
        self.assertIn("Pushing data to Pinot", joined)
        self.assertIn("Pushing data to Elastic", joined)
        self.assertIn(str(payload), joined)


if __name__ == "__main__":
    unittest.main()
