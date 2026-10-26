"""Shared helpers for static regression tests (stdlib only)."""

import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

OVERLAY_ENVIRONMENTS = ("dev", "stage", "qa", "prod")

EXPECTED_WORKLOAD_DEPLOYMENTS = (
    "kafka-ingest",
    "python-stream-processor",
    "spark-batch-processor",
    "realtime-processor",
    "ksqdb-connector",
    "serving-trino",
    "visualization-superset",
    "visualization-metabase",
    "data-catalog",
    "airflow",
)

OVERLAY_REPLICA_EXPECTATIONS = {
    "dev": 1,
    "stage": 2,
    "qa": 2,
    "prod": 3,
}


def read_repo_file(relative_path: str) -> str:
    return (REPOSITORY_ROOT / relative_path).read_text()


def deployment_replicas_from_patch(patch_text: str) -> dict[str, int]:
    """Parse strategic-merge patch YAML documents for deployment replica counts."""
    replicas: dict[str, int] = {}
    for document in patch_text.split("---"):
        name_match = re.search(
            r"^metadata:\s*\n\s*name:\s*(\S+)",
            document,
            flags=re.MULTILINE,
        )
        replica_match = re.search(
            r"^spec:\s*\n\s*replicas:\s*(\d+)",
            document,
            flags=re.MULTILINE,
        )
        if name_match and replica_match:
            replicas[name_match.group(1)] = int(replica_match.group(1))
    return replicas


def overlay_image_tag(kustomization_text: str) -> str:
    tags = re.findall(r'newTag:\s*"([^"]+)"', kustomization_text)
    if not tags:
        raise AssertionError("overlay kustomization has no image newTag entries")
    unique = set(tags)
    if len(unique) != 1:
        raise AssertionError(f"overlay uses inconsistent image tags: {sorted(unique)}")
    return tags[0]
