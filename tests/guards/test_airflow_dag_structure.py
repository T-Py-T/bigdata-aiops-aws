import ast
import unittest

from tests.guards.support import read_repo_text


class AirflowDagStructureTests(unittest.TestCase):
    def test_dag_declares_daily_schedule_and_linear_dependencies(self):
        source = read_repo_text("infra", "airflow", "dags", "pipeline_dag.py")
        tree = ast.parse(source)

        dag_assignments = [
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "dag" for target in node.targets)
        ]
        self.assertEqual(len(dag_assignments), 1)

        dag_call = dag_assignments[0].value
        self.assertIsInstance(dag_call, ast.Call)
        dag_keywords = {kw.arg: kw.value for kw in dag_call.keywords}
        self.assertEqual(dag_call.args[0].value, "data_pipeline")
        self.assertEqual(dag_keywords["schedule"].value, "@daily")
        self.assertFalse(dag_keywords["catchup"].value)

        self.assertIn("task_ingest >> task_stream >> task_batch", source)

    def test_bash_tasks_target_ingest_stream_and_batch_services(self):
        source = read_repo_text("infra", "airflow", "dags", "pipeline_dag.py")
        self.assertIn("http://kafka-ingest:8000/ingest", source)
        self.assertIn("python /app/processor.py", source)
        self.assertIn("spark-submit", source)
        self.assertIn("batch_processor.py", source)


if __name__ == "__main__":
    unittest.main()
