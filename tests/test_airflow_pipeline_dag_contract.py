import ast
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DAG_PATH = REPOSITORY_ROOT / "infra/airflow/dags/pipeline_dag.py"


class AirflowPipelineDagContractTests(unittest.TestCase):
    def test_dag_declares_daily_schedule_and_linear_task_chain(self) -> None:
        source = DAG_PATH.read_text()
        tree = ast.parse(source, filename=str(DAG_PATH))

        dag_call = next(
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "dag" for target in node.targets)
        )
        self.assertIsInstance(dag_call.value, ast.Call)
        dag_keywords = {kw.arg: kw.value for kw in dag_call.value.keywords}
        self.assertEqual(ast.literal_eval(dag_keywords["schedule"]), "@daily")
        self.assertFalse(ast.literal_eval(dag_keywords["catchup"]))

        task_ids = []
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            if not any(isinstance(target, ast.Name) and target.id.startswith("task_") for target in node.targets):
                continue
            call = node.value
            self.assertIsInstance(call, ast.Call)
            task_id_kw = next(kw for kw in call.keywords if kw.arg == "task_id")
            task_ids.append(ast.literal_eval(task_id_kw.value))

        self.assertEqual(
            task_ids,
            ["run_ingest", "run_stream_processor", "run_batch_processor"],
        )
        self.assertIn("task_ingest >> task_stream >> task_batch", source)
        self.assertIn("http://kafka-ingest:8000/ingest", source)


if __name__ == "__main__":
    unittest.main()
