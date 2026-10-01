<!-- CONTRIBUTING.md -->
<!-- Points contributors to README validation steps and private security reporting. -->
<!-- It does not define governance committees, SLAs, or production support obligations. -->

# Contributing

This repository is an AWS big-data and AIOps **lab scaffold**. Prefer small,
focused pull requests that match the boundaries described in [README.md](README.md).

## Before you open a pull request

1. Read **Configure an environment** and **Generate a fresh scaffold** in
   [README.md](README.md).
2. Run the checks that match your edit:
   - `bash -n create_project.sh` and the Terraform/Kubernetes dry-run commands in README
     when you touch `infra/` or `create_project.sh`
   - `python3 -m unittest discover -s tests -v` when you change services or tests
   - `pre-commit run --all-files` when hooks apply to your paths
3. Do not commit credentials, AWS account identifiers, private endpoints, or
   decrypted configuration. Use placeholders and synthetic data in examples.

Describe what changed and why in the pull request. There is no separate issue
template or maintainer roster.

## Security

Use the private route in [SECURITY.md](SECURITY.md) for suspected vulnerabilities.
Do not post exploit details, live hostnames, or account-specific values in a
public issue.

## Related documentation

- [.github/dependabot.yml](.github/dependabot.yml) — scheduled dependency updates; tip-cite guidance (tip ≠ READY)
- [docs/HIREABILITY.md](docs/HIREABILITY.md) — topics, skim paths, and doc map for reviewers
- [SECURITY.md](SECURITY.md) — vulnerability reporting and repository boundary
- [LICENSE](LICENSE) — MIT terms

**Tip cite:** `a74eb828` (Ship 256 merge on `main`); steward remap pending resolve for
this documentation packet when this pull request merges.
