"""Shared helpers for repository guard tests (stdlib-only at import time)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Iterable

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def repo_path(*parts: str) -> Path:
    return REPOSITORY_ROOT.joinpath(*parts)


def read_repo_text(*parts: str) -> str:
    return repo_path(*parts).read_text(encoding="utf-8")


def load_module_from_path(
    relative_path: str,
    module_name: str,
    stub_modules: dict[str, ModuleType] | None = None,
) -> ModuleType:
    """Import a service module while optional third-party deps are stubbed out."""
    if stub_modules:
        for name, module in stub_modules.items():
            sys.modules[name] = module

    file_path = repo_path(relative_path)
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def deployment_replica_map(patch_yaml: str) -> dict[str, int]:
    import yaml

    documents = yaml.safe_load_all(patch_yaml)
    replicas: dict[str, int] = {}
    for document in documents:
        if not document:
            continue
        name = document["metadata"]["name"]
        replicas[name] = document["spec"]["replicas"]
    return replicas


def terraform_output_names(outputs_tf: str) -> set[str]:
    names: set[str] = set()
    for line in outputs_tf.splitlines():
        stripped = line.strip()
        if stripped.startswith("output "):
            names.add(stripped.split('"')[1])
    return names


def terraform_variable_defaults(variables_tf: str) -> dict[str, str | None]:
    """Return variable name -> default literal text, or None when required."""
    import re

    blocks = re.findall(
        r'variable\s+"(?P<name>[^"]+)"\s*\{(?P<body>.*?)\}',
        variables_tf,
        flags=re.DOTALL,
    )
    defaults: dict[str, str | None] = {}
    for name, body in blocks:
        match = re.search(r"default\s*=\s*(?P<value>.+)", body)
        defaults[name] = match.group("value").strip() if match else None
    return defaults


def overlay_names() -> Iterable[str]:
    overlays_root = repo_path("infra", "k8s", "overlays")
    return sorted(path.name for path in overlays_root.iterdir() if path.is_dir())
