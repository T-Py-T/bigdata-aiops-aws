# Hireability and discoverability

This file is a thin index for reviewers, recruiters, and contributors who land
on the repository from search or a portfolio link. It does not change runtime
behavior; remove or trim it without affecting the scaffold.

**Tip cite:** `b045787` (current `main` prefix at authoring time); steward remap
pending resolve for the docs-only PR that introduced this page.

## What to skim first

| If you want… | Start here |
| --- | --- |
| Platform scope and layout | [README](../README.md) |
| Placeholders, validation, local checks | [Adapting the scaffold](adapting-the-scaffold.md) |
| Vulnerability reporting | [SECURITY](../SECURITY.md) |
| Terms of use | [MIT License](../LICENSE) |

There is no separate `CONTRIBUTING.md`; use pull requests against `main` and
follow the security boundary in [SECURITY](../SECURITY.md) for sensitive reports.

## Topics and skills surfaced here

The repository is tagged on GitHub for discoverability around **AWS**, **EKS**,
**Kubernetes**, **Terraform**, **Argo CD**, and **data-platform** layout. The
scaffold also touches **Kafka** ingestion, **Spark** batch and streaming,
**Trino** serving, **Airflow** orchestration, **Prometheus/Grafana**
observability, and **GitOps** (Kustomize overlays).

That combination is useful to cite when describing **big-data platform**
engineering, **AIOps-style** lab automation, or **streaming** reference
architectures—not as a production product claim.

## Adjacent application theme (Ship 255 pairing)

Batch and streaming boundaries here are a common place to land features before
an **application layer** (for example retrieval-augmented or API-facing
services) consumes curated data from Trino, catalogs, or object storage. This
repo stays at the **platform scaffold** layer; pair it mentally with
application-focused work rather than expecting RAG or app code in-tree.

## Reversibility

Delete this file and any README cross-links that point to it to revert the
hireability lean without touching infrastructure or services.
