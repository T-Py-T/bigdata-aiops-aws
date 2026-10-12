"""Helpers for loading repository files and service modules under test."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Callable
from unittest.mock import MagicMock

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def read_repo_file(*parts: str) -> str:
    return (REPOSITORY_ROOT.joinpath(*parts)).read_text()


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


def load_module(
    module_name: str,
    relative_source: str,
    *,
    stubs: dict[str, object],
) -> ModuleType:
    saved = {name: sys.modules.get(name) for name in stubs}
    try:
        for name, value in stubs.items():
            sys.modules[name] = value  # type: ignore[assignment]

        source_path = REPOSITORY_ROOT / relative_source
        spec = importlib.util.spec_from_file_location(module_name, source_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Unable to load module from {source_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        for name, previous in saved.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous


def parse_properties_file(content: str) -> dict[str, str]:
    properties: dict[str, str] = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, value = stripped.split("=", 1)
        properties[key.strip()] = value.strip()
    return properties
