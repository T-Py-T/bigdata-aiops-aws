import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def service_src(service_name: str) -> Path:
    return REPOSITORY_ROOT / "services" / service_name / "src"


def import_service_module(service_name: str, module_name: str):
    src = service_src(service_name)
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    return __import__(module_name)
