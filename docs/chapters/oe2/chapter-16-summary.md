# Chapter 16: Telemetry pipelines

Part 4: Technical deep dives. Coverage: Read in full from the book; text paraphrased.

## Summary

Mike Kelly (Bindplane): treat the flow of telemetry as its own concern. Stages: collect → normalize & secure → enrich → reduce → route, underpinned by resilience and a control plane.

Built on the OTel Collector (receivers, processors, exporters, extensions). The same binary runs as a lightweight agent near workloads and as gateway clusters doing the heavy lifting. Fleets are managed with OpAMP.

Agent + gateway is the default production pattern. Multi-tier (local then regional gateways) suits large estates.

## Key ideas

- Normalize to OTLP. Redact PII and enforce residency (GDPR, FedRAMP, HIPAA) before data leaves. Enrich with k8s, business and geo/DNS lookups.
- Reduce by filtering, deduplicating, aggregating and sampling. Route by fan-out (SIEM, APM, analytics, archive). Adding a tool becomes a config change.
- Resilience: buffers per stage with disk persistence, retries with exponential backoff, backpressure, HA agents and gateways.
- Migration: start greenfield, then redirect existing agents to gateways, then replace them. Fragile legacy can stay in phase 2.
- Evidence: 20–40% of SIEM data is never queried. One customer had 25,000+ collectors drifting. Savings of 50%+ are common; one customer avoided a $2.6M overage. Save 50%, reinvest 10%, net about 40%.

## You will learn

- Name the pipeline stages and resilience features
- Choose agent-only, agent+gateway or multi-tier
- Plan a phased migration and make the ROI case

## Claims and numbers

| Figure | Context |
|---|---|
| >100 | OTel Collector receivers |
| 20–40% | SIEM data never queried |
| 25,000+ | Collectors in one fleet |
| $2.6M | Overage eliminated |
| ~40% | Net savings after reinvesting 10% |

## Terms

| Term | Meaning |
|---|---|
| Gateway | Central Collector tier for processing/routing |
| Backpressure | Signal upstream to slow down when queues fill |
| Fan-out | Same telemetry to multiple destinations |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| OpAMP | Open Agent Management Protocol | AWS Systems Manager-like fleet mgmt |
| Bindplane | Commercial OTel control plane | Marketplace |
| SIEM | Security event management | Security Lake + OpenSearch/Splunk |

## Interview line

> I'd put a Collector gateway tier between apps and backends. It redacts PII once, enriches, samples and routes. That removes vendor coupling and lets security and observability share one clean stream. Agents stay light; gateways scale horizontally with queues.

## AWS mapping

- ADOT Collector DaemonSet + gateway Deployment behind NLB on EKS
- Kinesis Firehose → S3/OpenSearch; Security Lake for OCSF security data

## Practice question

**Q.** Finance says the SIEM bill doubled. What do you do in 30 days?

**Model answer.** Measure which sources and fields are actually queried. Put a gateway in front, drop or aggregate the never-queried streams, dedupe noisy logs, keep full fidelity only for detection-relevant events, archive the rest cheaply in S3. Report the before/after cost per GB and per detection.

## Exercise

Run pocs/07_telemetry_pipeline; add a route that sends only ERROR logs to a 'pager' destination.

## Takeaways

- Pipelines decouple producers from consumers
- Redact once, centrally
- Cut what nobody queries
