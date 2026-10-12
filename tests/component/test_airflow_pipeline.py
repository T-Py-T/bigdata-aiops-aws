import ast
import unittest

from component.support import REPOSITORY_ROOT


class AirflowPipelineTests(unittest.TestCase):
    def setUp(self):
        self.dag_path = REPOSITORY_ROOT / "infra" / "airflow" / "dags" / "pipeline_dag.py"
        self.source = self.dag_path.read_text()
        self.tree = ast.parse(self.source, filename=str(self.dag_path))

    def test_dag_id_and_schedule(self):
        self.assertIn("'data_pipeline'", self.source)
        self.assertIn("schedule='@daily'", self.source)
        self.assertIn("catchup=False", self.source)

    def test_task_dependencies_form_ingest_to_batch_chain(self):
        self.assertIn("task_ingest >> task_stream >> task_batch", self.source)

    def test_bash_operators_reference_runtime_services(self):
        self.assertIn("http://kafka-ingest:8000/ingest", self.source)
        self.assertIn("python /app/processor.py", self.source)
        self.assertIn("spark-submit --master local", self.source)

    def test_default_args_include_retries(self):
        default_args = next(
            node
            for node in self.tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "default_args"
                for target in node.targets
            )
        )
        self.assertIsInstance(default_args.value, ast.Dict)
        keys = {ast.literal_eval(key) for key in default_args.value.keys}
        self.assertIn("retries", keys)
        self.assertIn("retry_delay", keys)


if __name__ == "__main__":
    unittest.main()
