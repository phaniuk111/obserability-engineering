# Production-shaped Collector configs

Two tiers, because tail sampling decides per whole trace and so needs every span of a trace on one instance. The local lab (`../local.yaml`) is the same idea collapsed into one Collector.

| File | Role | What to notice |
|---|---|---|
| `agent-collector.yaml` | DaemonSet next to workloads | Kubernetes and cloud enrichment happens here; `load_balancing` routes by trace id |
| `gateway-collector.yaml` | Sampling tier | Scrub PII → RED metrics from 100% of spans → S3 archive of everything → tail sample → vendor |

```bash
python3 ../check_config.py                                   # structural lint (needs PyYAML)
otelcol-contrib validate --config=gateway-collector.yaml     # the real check, with a Collector binary
```

## Why each part is there, with the doc behind it

| Decision | Source |
|---|---|
| Tail sampling in its own pipeline behind a `forward` connector; span metrics are taken before it | [Tail sampling processor](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/processor/tailsamplingprocessor), [Span metrics connector](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/connector/spanmetricsconnector) |
| Agent tier with `load_balancing` and `routing_key: traceID` | [Load balancing exporter](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/exporter/loadbalancingexporter) |
| `sending_queue.storage` on the vendor exporter, backed by `file_storage` | [Collector resiliency](https://opentelemetry.io/docs/collector/resiliency/) |
| Exporter-level batching instead of the `batch` processor (deprecated) | [Deprecating the Collector batch processor](https://opentelemetry.io/blog/2026/collector-batching-migration/) |
| `sigv4auth` as the authenticator for Amazon Managed Service for Prometheus | [SigV4 auth extension](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/extension/sigv4authextension/README.md), [ADOT SigV4 guide](https://aws-otel.github.io/docs/sigv4) |
| `otlp_http` exporter id (`otlphttp` is a deprecated alias) | [OTLP/HTTP exporter](https://pkg.go.dev/go.opentelemetry.io/collector/exporter/otlphttpexporter) |
| Unsampled traces to S3, so a dropped trace can still be found | [AWS S3 exporter](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/exporter/awss3exporter) |

Not verified: these two files were checked against the documentation above and by the lint, not run through a Collector binary. Component ids and keys change between releases, so run `validate` on the version you deploy.
