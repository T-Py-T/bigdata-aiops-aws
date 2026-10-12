#!/bin/bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 [deploy|destroy]"
  exit 1
fi

terraform_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
COMMAND="$1"

terraform -chdir="$terraform_directory" init

if [ "$COMMAND" == "deploy" ]; then
  echo "Planning deployment..."
  terraform -chdir="$terraform_directory" plan -out=tfplan
  echo "Applying plan..."
  terraform -chdir="$terraform_directory" apply -auto-approve tfplan
elif [ "$COMMAND" == "destroy" ]; then
  echo "Destroying infrastructure..."
  terraform -chdir="$terraform_directory" destroy -auto-approve
else
  echo "Unknown command: $COMMAND"
  echo "Usage: $0 [deploy|destroy]"
  exit 1
fi
