# Lab 8: from lab to production (ch16, ch29–31)

No commands to run here: read two files side by side.

| Concern | Lab (`collector/local.yaml`) | Production (`collector/production/`) |
|---|---|---|
| Tail sampling with several Collectors | One Collector, so nothing to route | Agent tier with `load_balancing` by trace id in front of the sampling tier |
| Losing data on restart | In-memory queue | `sending_queue.storage: file_storage/queue` on disk |
| Batching | `batch` processor (pinned older release) | Exporter-level `sending_queue.batch`; the processor is [deprecated](https://opentelemetry.io/blog/2026/collector-batching-migration/) |
| Full-fidelity store | ClickHouse `otel_traces` | S3 via `awss3` exporter, lifecycle rules in `aws/terraform` |
| Metrics | Prometheus scrape | Remote write to Amazon Managed Service for Prometheus with `sigv4auth` |
| Kubernetes metadata | None | `k8sattributes` + `resourcedetection` on the agent |
| Watching the Collector | `:13133` and `:8889` | CloudWatch alarms on failed exports **and** on silence (`aws/terraform`) |

## AWS mapping

| Lab piece | On AWS |
|---|---|
| OTel SDK + Collector | AWS Distro for OpenTelemetry (ADOT), or the CloudWatch agent, which is built on the Collector |
| Jaeger | CloudWatch Application Signals and Transaction Search over [OTLP endpoints](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-OTLPEndpoint.html) (X-Ray SDKs and daemon are in maintenance; AWS points to OpenTelemetry) |
| ClickHouse wide events | ClickHouse Cloud on AWS, or S3 + Athena for cold data |
| Prometheus + rules | Amazon Managed Service for Prometheus; Application Signals SLOs |
| Grafana | Amazon Managed Grafana |
| Fault toggle | AppConfig feature flags |

**Interview drill: "Design telemetry for 200 services on EKS."** Use the table as your outline: SDK defaults in a shared library, agent DaemonSet for enrichment, gateway for policy (PII, sampling, routing), metrics before sampling, a cheap complete archive, durable queues, alarms on the pipeline itself, and OpenTelemetry throughout so the backend can change.
