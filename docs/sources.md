# Official documentation used in the review

Checked on 2026-11-27. Per-chapter links also appear in each chapter summary and lesson.

## ch06 Making structured events arbitrarily wide

- [W3C Trace Context](https://www.w3.org/TR/trace-context/): The traceparent and tracestate headers, field by field

## ch07 Instrumenting with OpenTelemetry

- [OpenTelemetry semantic conventions: HTTP spans](https://opentelemetry.io/docs/specs/semconv/http/http-spans): Stable attribute names such as http.request.method
- [HTTP conventions migration guide](https://opentelemetry.io/docs/specs/semconv/http/migration-guide/): Old name → new name table
- [OpenTelemetry eBPF Instrumentation (OBI)](https://opentelemetry.io/docs/zero-code/obi/): Zero-code instrumentation from the kernel
- [Weaver](https://github.com/open-telemetry/weaver): Define, lint and live-check telemetry schemas
- [AWS: migrating from X-Ray SDKs to OpenTelemetry](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-migration.html): Concept mapping and timeline

## ch10 AI agents for observability

- [Amazon CloudWatch investigations (GA announcement)](https://aws.amazon.com/about-aws/whats-new/2025/06/ga-accelerate-troubleshooting-amazon-cloudwatch-investigations): AWS's AI-assisted investigation feature

## ch12 Acting on SLO burn alerts

- [Google SRE Workbook: Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/): Multi-window, multi-burn-rate alerts

## ch14 Storage: ClickHouse

- [ClickHouse MergeTree engine](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree): Parts, granules, sparse primary index
- [MergeTree settings: max_bytes_*](https://clickhouse.com/docs/reference/settings/merge-tree-settings/max-bytes): Where the 150 GB merged-part default comes from
- [Collector ClickHouse exporter](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/exporter/clickhouseexporter): The otel_traces schema used in the lab

## ch15 Cheap and accurate enough sampling

- [OpenTelemetry: Sampling](https://opentelemetry.io/docs/concepts/sampling/): Head vs tail, when to sample at all
- [Tail sampling processor](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/processor/tailsamplingprocessor): Policies, decision_wait, scaling
- [Load balancing exporter](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/exporter/loadbalancingexporter): Routing by trace id in front of tail sampling

## ch16 Telemetry pipelines

- [Collector resiliency](https://opentelemetry.io/docs/collector/resiliency/): Sending queue, retries, persistent storage
- [Deprecating the Collector batch processor](https://opentelemetry.io/blog/2026/collector-batching-migration/): Exporter-level batching
- [Span metrics connector](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/connector/spanmetricsconnector): RED metrics from spans
- [OpAMP specification](https://opentelemetry.io/docs/specs/opamp): Remote management of agent fleets
- [CloudWatch OTLP endpoints](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-OTLPEndpoint.html): Sending OTLP straight to AWS, SigV4-signed

## ch18 Observability for CI/CD

- [OpenTelemetry semantic conventions: CI/CD](https://opentelemetry.io/docs/specs/semconv/cicd/): Pipeline run and task spans

## ch21 Observability for LLM applications

- [GenAI semantic conventions: spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/): gen_ai.* attributes for model calls
- [GenAI conventions repository](https://github.com/open-telemetry/semantic-conventions-genai): Where the gen_ai.* definitions now live

## ch29 Build vs buy vs open source

- [AWS services in maintenance](https://docs.aws.amazon.com/general/latest/gr/maintenance_services.html): Check before you depend on a managed service

## ch31 Instrumentation for observability teams

- [Build a custom Collector (OCB)](https://opentelemetry.io/docs/collector/extend/ocb/): Your own distribution from a manifest
- [Observability by design with Weaver](https://opentelemetry.io/blog/2025/otel-weaver/): Registry check, code generation, live check
- [Collector management with OpAMP](https://opentelemetry.io/docs/collector/management/): Central control of Collector config

## Also consulted

- [X-Ray SDK and daemon support timeline](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-daemon-timeline.html)
- [Support for CloudWatch Evidently ending](https://aws.amazon.com/blogs/mt/support-for-amazon-cloudwatch-evidently-ending-soon)
- [Amazon Pinpoint end of support](https://docs.aws.amazon.com/pinpoint/latest/userguide/migrate.html)
- [AWS Proton deprecation and migration guide](https://docs.aws.amazon.com/proton/latest/userguide/proton-end-of-support.html)
- [OTLP/HTTP exporter (component id note)](https://pkg.go.dev/go.opentelemetry.io/collector/exporter/otlphttpexporter)
- [Trace Context Level 2](https://www.w3.org/TR/trace-context-2/)
- [OpenTelemetry CI/CD observability announcement](https://opentelemetry.io/blog/2025/otel-cicd-sig/)
- [SigV4 authenticator extension](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/extension/sigv4authextension/README.md)
- [AWS S3 exporter](https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/exporter/awss3exporter)
- [CloudWatch and OpenTelemetry](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-OpenTelemetry-Sections.html)

## What changed since the book

- **ch06**: Trace flags are a bit field: only the lowest bit means 'sampled', and version `ff` is invalid. Trace Context Level 2 adds a 'random trace id' flag, so compare bits, not the string `01`.
- **ch07**: AWS put the X-Ray SDKs and daemon into maintenance on 25 Feb 2026, with end of support on 25 Feb 2027, and recommends OpenTelemetry instrumentation instead.
- **ch07**: The GenAI (`gen_ai.*`) conventions moved to their own repository in 2026 and are still marked as in development, so expect renames.
- **ch10**: The AWS feature previewed as 'Amazon Q Developer operational investigations' became generally available in June 2025 under the name CloudWatch investigations.
- **ch11**: Check the arithmetic in the chapter's LLM transcript: 99.95% availability allows about 4.4 hours of downtime a year (about 22 minutes a month), not the '~42 minutes' the model says. It makes the chapter's own point: treat the model as a draft generator and verify.
- **ch15**: Tail sampling only works if every span of a trace reaches the same Collector instance; with more than one, put a load-balancing tier that routes by trace id in front.
- **ch16**: The Collector's `batch` processor is deprecated in favour of batching inside each exporter's `sending_queue`; the project's timeline has it warning from v0.171 (Feb 2027) and removed in v0.177 (May 2027).
- **ch16**: The OTLP exporters are now called `otlp_grpc` and `otlp_http`; `otlp` and `otlphttp` remain as deprecated aliases.
- **ch18**: OpenTelemetry now has CI/CD semantic conventions (first attributes in v1.27.0), so pipeline traces can use standard names.
- **ch19**: CloudWatch Evidently was discontinued in October 2025 (AWS points to AppConfig feature flags) and Amazon Pinpoint support ended on 30 October 2026.
- **ch23**: AWS Proton support ended on 7 October 2026; AWS's migration guide points to Backstage-based options such as Harmonix.
- **ch31**: The chapter's examples use `db.system`; current convention docs use `db.system.name`. A schema check in CI is what catches this kind of drift.
