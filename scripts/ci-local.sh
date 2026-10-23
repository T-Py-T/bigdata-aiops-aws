#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VENV="${ROOT}/.venv-ci"

bash -n create_project.sh infra/terraform/deploy.sh infra/terraform/destroy.sh
python3 -m unittest discover -s tests -v

if ! command -v terraform >/dev/null 2>&1; then
  echo "error: terraform must be on PATH (install from https://developer.hashicorp.com/terraform/install)" >&2
  exit 1
fi

python3 -m venv "${VENV}"
"${VENV}/bin/python" -m pip install --disable-pip-version-check pip-audit==2.10.1
"${VENV}/bin/python" -m pip install --disable-pip-version-check \
  --requirement services/kafka_ingest/requirements.txt \
  --requirement services/ksqdb_connector/requirements.txt \
  --requirement services/python_stream_processor/requirements.txt
"${VENV}/bin/python" -c "import fastapi, kafka, requests, uvicorn"
"${VENV}/bin/pip-audit" --requirement services/kafka_ingest/requirements.txt
"${VENV}/bin/pip-audit" --requirement services/ksqdb_connector/requirements.txt
"${VENV}/bin/pip-audit" --requirement services/python_stream_processor/requirements.txt

terraform -chdir=infra/terraform fmt -check
terraform -chdir=infra/terraform init -backend=false -input=false
terraform -chdir=infra/terraform validate
