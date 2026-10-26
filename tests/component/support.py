import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def service_src(service_name: str) -> Path:
    return REPOSITORY_ROOT / "services" / service_name / "src"


def _install_dependency_stubs() -> None:
    if "kafka" not in sys.modules:
        kafka = types.ModuleType("kafka")
        kafka.KafkaProducer = MagicMock(name="KafkaProducer")
        kafka.KafkaConsumer = MagicMock(name="KafkaConsumer")
        sys.modules["kafka"] = kafka

    if "fastapi" not in sys.modules:
        fastapi = types.ModuleType("fastapi")

        class _Route:
            def __init__(self, path: str) -> None:
                self.path = path

        class FastAPI:
            def __init__(self) -> None:
                self.routes: list[_Route] = []

            def get(self, path: str):
                def decorator(fn):
                    self.routes.append(_Route(path))
                    return fn

                return decorator

            def post(self, path: str):
                def decorator(fn):
                    self.routes.append(_Route(path))
                    return fn

                return decorator

        fastapi.FastAPI = FastAPI
        sys.modules["fastapi"] = fastapi

    if "requests" not in sys.modules:
        sys.modules["requests"] = types.ModuleType("requests")


def import_service_module(service_name: str, module_name: str):
    """Load a service module without requiring third-party packages on PYTHONPATH."""
    _install_dependency_stubs()
    module_path = service_src(service_name) / f"{module_name}.py"
    qualified_name = f"test_services.{service_name}.{module_name}"
    spec = importlib.util.spec_from_file_location(qualified_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[qualified_name] = module
    spec.loader.exec_module(module)
    return module
