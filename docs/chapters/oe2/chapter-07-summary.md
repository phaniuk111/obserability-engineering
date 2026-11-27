# Chapter 7: Instrumenting with OpenTelemetry

Part 2: Instrumentation fundamentals. Coverage: Read in full from the book; text paraphrased.

## Summary

OTel is trace-first: context is the glue. Interprocess propagation (W3C TraceContext headers, baggage) and intraprocess propagation (scopes, thread-locals) mean any metric or log can be tied to the request that produced it.

Create a span when the work is interesting (it affects latency or failure) and aggregable (grouping by its name gives useful trends). HTTP handlers, DB queries, external calls, cache lookups and queue publish/consume: yes. Helpers, getters, loop iterations: no. A hundred 2 ms spans is too many.

Layer signals rather than duplicating them. Traces for causality, metrics for cheap long-term alerting, logs/events for rare or audited things. A span plus a histogram per HTTP request is a common pair.

## Key ideas

- Streaming: put context in the message envelope, use producer spans on publish and consumer spans connected by span links (not parent/child), and propagate a hashed correlation ID. Use metrics with exemplars for fleet alerting, e.g. failed/processed per stage and a publish-to-process histogram.
- Long jobs: avoid million-child traces. Model each stage as its own trace with links, or write one summary wide event at the end. Don't re-flush the root span; most stores can't update spans.
- Serverless: one well-designed span per invocation. On Lambda, emit lightweight events and assemble them in a stateful Collector (stateless tracing).
- eBPF via OBI captures HTTP/gRPC traces with no code changes. It fills gaps for legacy services but needs privileges.
- Naming: no IDs in names (GET /users/{user.id}), dot.case, units as metadata (http.server.request.duration, not ..._ms).
- Schemas with OTel Weaver validate telemetry in CI and generate helpers. Hash PII, use allowlists, and use transform processors.
- Agents: plan first, then execute in small steps. Have them write scripts that do the migration ('automate the automation'), diff old vs new telemetry, and check rules into git.

## You will learn

- Decide when to create a span (interesting + aggregable)
- Trace streaming, fan-out, long jobs, serverless and eBPF cases
- Layer signals deliberately and keep telemetry consistent with schemas

## Claims and numbers

| Figure | Context |
|---|---|
| 100 x 2 ms | Symptom of too many spans |
| >100 | Receivers in the OTel Collector (ch16) |

## Terms

| Term | Meaning |
|---|---|
| Trace-first | All signals tied to an active trace context |
| Layered telemetry | Right signal at the right detail for each consumer |
| Baggage | Key-values propagated with trace context |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| W3C TraceContext / baggage | Standard propagation header + key-values | ADOT propagators (xray + tracecontext) |
| Span links | Relate spans across traces (async) | OTel span links sent over OTLP (X-Ray SDKs are in maintenance; AWS points to OTel) |
| Exemplars | Metric point → trace/span pointer | CloudWatch/AMP exemplars |
| OBI (OTel eBPF Instrumentation) | Kernel-level zero-code tracing | EKS add-on style deployment |
| OTel Weaver | Schema-driven telemetry validation/codegen | n/a |
| Conway's law | Systems mirror org communication | n/a |

## Interview line

> For Kafka I don't nest consumers under producers. I inject context into the message, make a consumer span linked to the producer, and carry a business correlation ID through every stage. I alert on per-stage counters and publish-to-process histograms with exemplars.

## AWS mapping

- SQS/SNS/Kinesis: propagate traceparent in message attributes
- Lambda: ADOT layer or stateless events + Collector extension
- EKS: OBI DaemonSet

## Practice question

**Q.** A nightly ETL runs for 6 hours across thousands of supplier files. How do you instrument it?

**Model answer.** Not one giant trace. Each stage (extract, transform per batch, load) gets its own trace, joined by span links and a run ID. I'd emit progress metrics for live status, and at the end write a summary wide event with counts, failures by supplier and durations. Alerts go on stage failure ratio and runtime vs baseline.

## Exercise

Lab 1: read `lab/app/shop.py`, add one attribute and one custom span of your own, rebuild, and find them in ClickHouse. Explain why `send_receipt` uses a link, not a parent.

## Takeaways

- Context is the product
- Interesting + aggregable → span
- Layer, don't duplicate; schemas keep humans and AI aligned

## Hands-on

[Lab 1: Follow one request](https://github.com/phaniuk111/obserability-engineering/blob/main/lab/labs/01-traces.md)

## Since the book (checked against documentation, 2026-11-27)

- AWS put the X-Ray SDKs and daemon into maintenance on 25 Feb 2026, with end of support on 25 Feb 2027, and recommends OpenTelemetry instrumentation instead.
- The GenAI (`gen_ai.*`) conventions moved to their own repository in 2026 and are still marked as in development, so expect renames.

## Official documentation

- [OpenTelemetry semantic conventions: HTTP spans](https://opentelemetry.io/docs/specs/semconv/http/http-spans): Stable attribute names such as http.request.method
- [HTTP conventions migration guide](https://opentelemetry.io/docs/specs/semconv/http/migration-guide/): Old name → new name table
- [OpenTelemetry eBPF Instrumentation (OBI)](https://opentelemetry.io/docs/zero-code/obi/): Zero-code instrumentation from the kernel
- [Weaver](https://github.com/open-telemetry/weaver): Define, lint and live-check telemetry schemas
- [AWS: migrating from X-Ray SDKs to OpenTelemetry](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-migration.html): Concept mapping and timeline
