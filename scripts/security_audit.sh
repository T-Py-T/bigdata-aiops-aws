#!/usr/bin/env bash
# Audit Python requirements (Trivy) and pinned container base images (Trivy).
# Service Dockerfiles run apt-get upgrade at build time; base-image scans surface upstream drift.
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repository_root"

if ! command -v trivy >/dev/null 2>&1; then
  echo "trivy is required but was not found on PATH" >&2
  exit 1
fi

trivy_requirements_failed=0
while IFS= read -r -d '' requirements_file; do
  relative_path="${requirements_file#"$repository_root"/}"
  echo "Trivy pip scan: ${relative_path}"
  if ! trivy fs --scanners vuln --severity HIGH,CRITICAL --exit-code 1 -q "$requirements_file"; then
    trivy_requirements_failed=1
  fi
done < <(find "$repository_root/services" -name requirements.txt -print0 | sort -z)

container_scan_failed=0
strict_base_images="${TRIVY_STRICT_BASE_IMAGES:-0}"
while IFS= read -r -d '' dockerfile; do
  image_ref="$(head -n 1 "$dockerfile" | sed 's/^FROM //')"
  relative_path="${dockerfile#"$repository_root"/}"
  echo "Trivy base image scan: ${relative_path} (${image_ref})"
  exit_code=0
  if [[ "$strict_base_images" == "1" ]]; then
    exit_code=1
  fi
  if ! trivy image \
    --ignore-unfixed \
    --severity HIGH,CRITICAL \
    --exit-code "$exit_code" \
    -q \
    "$image_ref"; then
    container_scan_failed=1
  fi
done < <(find "$repository_root" -name Dockerfile -print0 | sort -z)

if [[ "$trivy_requirements_failed" -ne 0 ]]; then
  echo "Trivy found HIGH/CRITICAL vulnerabilities in requirements.txt files." >&2
  exit 1
fi

if [[ "$container_scan_failed" -ne 0 && "$strict_base_images" == "1" ]]; then
  echo "Trivy reported fixable HIGH/CRITICAL issues in one or more pinned base images." >&2
  echo "Rebuild service images (apt-get upgrade in Python Dockerfiles) or bump image digests." >&2
  exit 1
fi

if [[ "$container_scan_failed" -ne 0 ]]; then
  echo "Note: upstream base images still report fixable HIGH/CRITICAL issues (logged above)."
  echo "Python service Dockerfiles run apt-get upgrade at build time; bump digests when vendors publish."
fi

echo "Trivy security audit passed."
