#!/bin/bash
set -euo pipefail

terraform_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

terraform -chdir="$terraform_directory" init
terraform -chdir="$terraform_directory" destroy "$@"
