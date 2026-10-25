import unittest

from tests.coverage.support import parse_properties_file, read_repo_file


class TrinoCoordinatorConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.properties = parse_properties_file(
            read_repo_file("services", "serving_trino", "config", "config.properties")
        )

    def test_coordinator_role_is_enabled(self) -> None:
        self.assertEqual(self.properties["coordinator"], "true")
        self.assertEqual(self.properties["node-scheduler.include-coordinator"], "true")

    def test_http_and_discovery_endpoints_align(self) -> None:
        self.assertEqual(self.properties["http-server.http.port"], "8080")
        self.assertEqual(self.properties["discovery.uri"], "http://localhost:8080")

    def test_query_memory_limits_are_declared(self) -> None:
        self.assertEqual(self.properties["query.max-memory"], "5GB")
        self.assertEqual(self.properties["query.max-memory-per-node"], "1GB")


if __name__ == "__main__":
    unittest.main()
