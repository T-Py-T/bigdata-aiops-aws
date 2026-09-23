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
