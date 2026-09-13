# Adapting the scaffold

The checked-in tree is a generator output, not a configured deployment. Copy it
into a new working directory, then replace its inputs from the outside in.

## 1. Choose the platform boundary

Decide which included services the environment actually needs. Remove unused
workloads from `infra/k8s/base/kustomization.yaml` before creating images or
cloud resources. The scaffold deliberately keeps ingestion, processing,
serving, catalog, dashboards, and orchestration separate so each can be
replaced independently.

## 2. Update infrastructure versions

The AWS provider, VPC module, EKS module, and Kubernetes version are pinned in
`infra/terraform/`. Review their upgrade notes before changing those pins, then
replace the sample network ranges, sizing, and tags through Terraform variables.

Run formatting before initialization:

```bash
terraform -chdir=infra/terraform fmt -check
terraform -chdir=infra/terraform init -backend=false
terraform -chdir=infra/terraform validate
```

`init` downloads providers and modules. It does not create AWS resources.
Inspect `terraform plan` separately with the intended AWS account and region
before any apply.

## 3. Build and pin images

Every application placeholder in the Kubernetes base needs a concrete image
repository. Build only the selected services, scan the resulting images, and
pin each environment to an immutable digest.

The image placeholders are:

- `AIRFLOW_IMAGE`
- `DATA_CATALOG_IMAGE`
- `KAFKA_INGEST_IMAGE`
- `KSQLDB_CONNECTOR_IMAGE`
- `PYTHON_STREAM_PROCESSOR_IMAGE`
- `REALTIME_PROCESSOR_IMAGE`
- `SERVING_TRINO_IMAGE`
- `SPARK_BATCH_PROCESSOR_IMAGE`
- `VISUALIZATION_METABASE_IMAGE`
- `VISUALIZATION_SUPERSET_IMAGE`

## 4. Supply runtime endpoints

Replace the remaining placeholders with environment-specific values:

| Placeholder | Used for |
| --- | --- |
| `KAFKA_BROKER` | Ingest producer and Python consumer connection |
| `S3_BUCKET` | Spark batch and streaming inputs |
| `PINOT_ENDPOINT` | Example serving connector |
| `ELASTIC_ENDPOINT` | Connector and catalog configuration |
| `REPO_URL` | Argo CD source repository |
| `K8S_API_SERVER` | Argo CD destination cluster |

Find unresolved inputs with:

```bash
rg -n '\{\{' infra services
```

Do not commit credentials. Use the AWS credential chain and the environment's
secret manager for tokens, passwords, and application secrets.

Create `bigdata-platform-secrets` in the target namespace with a strong
`superset-secret-key` value before deploying Superset. The checked-in
deployment reads the value through a Kubernetes Secret reference; it does not
contain a default application secret.

## 5. Render before applying

After every placeholder has been replaced:

```bash
kubectl kustomize infra/k8s/overlays/dev > /tmp/streaming-platform-dev.yaml
kubectl apply --dry-run=client -f /tmp/streaming-platform-dev.yaml
```

Review the rendered image names, namespaces, resource requests, service
accounts, network exposure, and secret references. Repeat for the intended
overlay before registering the Argo CD application.

## Validation boundary

The commands above establish that the generator script parses, Terraform can
load the chosen modules, and Kubernetes can render the configured resources.
They do not establish service compatibility, data correctness, security,
performance, or recovery. Validate those properties with a synthetic event and
an environment-specific test plan after the selected services are deployed.
