<!-- SECURITY.md -->
<!-- Explains how to report a suspected vulnerability without publishing sensitive details. -->
<!-- It does not promise a response time, support contract, or deployed security posture. -->

# Security policy

## Report a vulnerability

Do not include credentials, hostnames, private addresses, AWS account IDs, or
configuration in a public issue. Use GitHub's private vulnerability reporting
when the repository Security tab offers it. If that option is unavailable,
email tnt850910@aol.com before sharing sensitive details.

Include the affected file or module, the expected behavior, and the minimum
steps needed to reproduce the problem with synthetic data.

We aim to acknowledge valid reports within a few business days. That is an
acknowledgment window, not a commitment to fix or disclose on a fixed schedule.

## Supported versions

Security fixes apply to the current `main` branch. Older tags and forks are
unsupported unless explicitly noted in a release.

## Repository boundary

This repository is an AWS big-data and AIOps lab scaffold: Terraform for local
or lab infrastructure, Kubernetes manifests, Argo CD, Airflow, and example
Python and Spark services. It is not a hosted SaaS and does not operate
production workloads on behalf of users.

Runtime secrets, AWS credentials, and environment-specific values belong
outside the repository. Never commit secret values, decrypted configuration,
private endpoints, or billable-resource identifiers tied to a real account.

The scaffold uses placeholder template values and synthetic validation paths.
Terraform and Kubernetes checks are intended for review before provisioning lab
resources, not for exposing a public attack surface.

There is no bug bounty, paid reward, or guaranteed response timeline beyond the
acknowledgment window above.

## Related documentation

- [README.md](README.md) — scaffold scope, configuration, validation, and deployment order
- [docs/HIREABILITY.md](docs/HIREABILITY.md) — thin reviewer and discoverability index
- [CONTRIBUTING.md](CONTRIBUTING.md) — pull-request expectations for docs and scaffold changes
- [LICENSE](LICENSE) — MIT terms

**Tip cite:** `a74eb828` (Ship 256 merge on `main`); steward remap pending resolve for
this documentation packet when this pull request merges.
