"""Load service modules under tests/ without installing their runtime dependencies."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Callable
from unittest.mock import MagicMock

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class RouteRecordingApp:
    """Minimal FastAPI stand-in that records registered routes."""

    def __init__(self) -> None:
        self.routes: dict[tuple[str, str], Callable[..., object]] = {}

    def get(self, path: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
        def decorator(handler: Callable[..., object]) -> Callable[..., object]:
            self.routes[("GET", path)] = handler
            return handler

        return decorator

    def post(self, path: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
        def decorator(handler: Callable[..., object]) -> Callable[..., object]:
            self.routes[("POST", path)] = handler
            return handler

        return decorator


def _load_module(module_name: str, source_path: Path, *, stubs: dict[str, object]) -> ModuleType:
    for name, value in stubs.items():
        sys.modules[name] = value  # type: ignore[assignment]

    spec = importlib.util.spec_from_file_location(module_name, source_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {source_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_kafka_ingest_module() -> tuple[ModuleType, RouteRecordingApp]:
    app = RouteRecordingApp()
    fastapi = MagicMock()
    fastapi.FastAPI.return_value = app
    module = _load_module(
        "kafka_ingest_under_test",
        REPOSITORY_ROOT / "services/kafka_ingest/src/ingest.py",
        stubs={"fastapi": fastapi, "kafka": MagicMock()},
    )
    return module, app


def load_stream_processor_module() -> ModuleType:
    return _load_module(
        "stream_processor_under_test",
        REPOSITORY_ROOT / "services/python_stream_processor/src/processor.py",
        stubs={"kafka": MagicMock()},
    )


def load_ksqdb_connector_module() -> ModuleType:
    return _load_module(
        "ksqdb_connector_under_test",
        REPOSITORY_ROOT / "services/ksqdb_connector/src/connector.py",
        stubs={"requests": MagicMock()},
    )
