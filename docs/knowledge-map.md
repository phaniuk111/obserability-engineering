# Knowledge map

Themes → concepts → one-line definition → chapters → POC.

## Foundations

| Concept | Definition | Chapters | POC |
|---|---|---|---|
| Observability as dependability | Understand or debug any system state, even novel ones | ch01, ch03 | — |
| Cardinality & dimensionality | Distinct values per field; number of fields; both raise value combinatorially | ch01, ch05, ch06, ch13 | 01_wide_events |
| Three pillars vs unified storage | Separate silos for infra vs one wide-event store for your code | ch01, ch03, ch25, ch26 | 06_columnar_store |
| Known vs unknown unknowns | Thresholds catch what you predicted; exploration catches the rest | ch03, ch11 | — |

## Instrumentation

| Concept | Definition | Chapters | POC |
|---|---|---|---|
| Wide structured events | One flat, context-rich record per unit of work | ch05, ch06, ch07, ch28 | 01_wide_events |
| Tracing & context propagation | Spans with trace/span/parent IDs; W3C traceparent; links for async | ch05, ch07, ch18, ch22 | 02_mini_tracer |
| Auto vs custom instrumentation | Framework coverage plus business context | ch04, ch07, ch09, ch10 | — |
| Semantic conventions & schemas | Shared names and meaning; Weaver; ontologies | ch07, ch11, ch17, ch21 | 08_ai_sandwich |
| Sampling | Keep representative events with their rate; consistent, per-key, tail | ch04, ch07, ch15, ch27 | 05_sampling |

## Analysis & alerting

| Concept | Definition | Chapters | POC |
|---|---|---|---|
| Core analysis loop | Visualise, diff anomaly vs baseline, filter, repeat | ch08, ch09, ch12 | 03_bubbleup |
| SLOs & event-based SLIs | Alert on user pain; classify each eligible event good/bad | ch11, ch12, ch21, ch22, ch26 | 04_slo_burn |
| Burn-rate forecasting | Project baseline ×≤4 into lookahead; multiple windows | ch12 | 04_slo_burn |
| Observability-driven development | Ship features with the telemetry to validate them | ch02, ch09, ch23, ch25 | — |
| Profiling alongside tracing | Telescope (traces) then microscope (profiles) | ch09, ch20 | — |

## Delivery & feedback loops

| Concept | Definition | Chapters | POC |
|---|---|---|---|
| Deploy vs release; progressive delivery | Flags decouple; canaries need cohort comparison | ch02, ch09, ch26 | — |
| CI/CD as production | Workflows as traces; critical path; flake rate SLI | ch18, ch09 | 09_cost_and_ci |
| Feedback loops (amplifying/balancing) | Observability is the sense mechanism of every delivery loop | ch02, ch24, ch25 | — |
| Learning speed as constraint | With AI, validation not code generation limits delivery | ch01, ch03, ch23, ch25 | — |

## Data platform

| Concept | Definition | Chapters | POC |
|---|---|---|---|
| Columnar segments & read-time aggregation | Time-partitioned column files; prune; parallel scan; top-K | ch13, ch14 | 06_columnar_store |
| ClickHouse MergeTree | Sorted immutable parts, sparse index, lazy materialisation | ch14 | — |
| Telemetry pipelines | Collect, normalize, secure, enrich, reduce, route; agent+gateway | ch04, ch16, ch27 | 07_telemetry_pipeline |
| Tiered telemetry & attribution | Fidelity by criticality; cost per request/team | ch24, ch27, ch29 | 09_cost_and_ci |

## AI and new domains

| Concept | Definition | Chapters | POC |
|---|---|---|---|
| Agent context layer | Topology, names, deploys, incidents, business context for agents | ch08, ch10, ch23 | — |
| AI sandwich & invariants | Deterministic validation around nondeterministic proposals | ch17, ch21 | 08_ai_sandwich |
| LLM evals flywheel | Traces → evals → harness fixes → telemetry | ch17, ch21, ch22 | 08_ai_sandwich |
| Mobile: local buffer + control plane | Log locally; server rules decide what to upload | ch19 | 10_mobile_ring_buffer |
| User-focused SLIs | Intention → outcome (checkout completion, TTFT, resolution) | ch19, ch22 | 10_mobile_ring_buffer |

## Organisation & economics

| Concept | Definition | Chapters | POC |
|---|---|---|---|
| Sociotechnical debt | Misaligned culture/process and technology | ch23, ch24 | — |
| Observability as platform product | Paved paths, devs as customers, report to engineering | ch04, ch23, ch26, ch28, ch29 | — |
| Business case & diagnosis | Ops loop = cost center; dev loop = investment; leading indicators | ch26, ch27 | — |
| Change management | Five tests, coalition, mandate, one deep domain | ch28 | — |
| Build vs buy vs OSS | 2×2; price the puppy; buy platform, build glue | ch16, ch29 | 09_cost_and_ci |

