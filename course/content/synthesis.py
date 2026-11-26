"""Cross-chapter synthesis: one source for docs and course."""

# theme -> [(concept, one-line definition, [chapters], poc)]
KNOWLEDGE_MAP = [
 ("Foundations", [
  ("Observability as dependability", "Understand or debug any system state, even novel ones", ["ch01", "ch03"], None),
  ("Cardinality & dimensionality", "Distinct values per field; number of fields; both raise value combinatorially", ["ch01", "ch05", "ch06", "ch13"], "01_wide_events"),
  ("Three pillars vs unified storage", "Separate silos for infra vs one wide-event store for your code", ["ch01", "ch03", "ch25", "ch26"], "06_columnar_store"),
  ("Known vs unknown unknowns", "Thresholds catch what you predicted; exploration catches the rest", ["ch03", "ch11"], None),
 ]),
 ("Instrumentation", [
  ("Wide structured events", "One flat, context-rich record per unit of work", ["ch05", "ch06", "ch07", "ch28"], "01_wide_events"),
  ("Tracing & context propagation", "Spans with trace/span/parent IDs; W3C traceparent; links for async", ["ch05", "ch07", "ch18", "ch22"], "02_mini_tracer"),
  ("Auto vs custom instrumentation", "Framework coverage plus business context", ["ch04", "ch07", "ch09", "ch10"], None),
  ("Semantic conventions & schemas", "Shared names and meaning; Weaver; ontologies", ["ch07", "ch11", "ch17", "ch21"], "08_ai_sandwich"),
  ("Sampling", "Keep representative events with their rate; consistent, per-key, tail", ["ch04", "ch07", "ch15", "ch27"], "05_sampling"),
 ]),
 ("Analysis & alerting", [
  ("Core analysis loop", "Visualise, diff anomaly vs baseline, filter, repeat", ["ch08", "ch09", "ch12"], "03_bubbleup"),
  ("SLOs & event-based SLIs", "Alert on user pain; classify each eligible event good/bad", ["ch11", "ch12", "ch21", "ch22", "ch26"], "04_slo_burn"),
  ("Burn-rate forecasting", "Project baseline ×≤4 into lookahead; multiple windows", ["ch12"], "04_slo_burn"),
  ("Observability-driven development", "Ship features with the telemetry to validate them", ["ch02", "ch09", "ch23", "ch25"], None),
  ("Profiling alongside tracing", "Telescope (traces) then microscope (profiles)", ["ch09", "ch20"], None),
 ]),
 ("Delivery & feedback loops", [
  ("Deploy vs release; progressive delivery", "Flags decouple; canaries need cohort comparison", ["ch02", "ch09", "ch26"], None),
  ("CI/CD as production", "Workflows as traces; critical path; flake rate SLI", ["ch18", "ch09"], "09_cost_and_ci"),
  ("Feedback loops (amplifying/balancing)", "Observability is the sense mechanism of every delivery loop", ["ch02", "ch24", "ch25"], None),
  ("Learning speed as constraint", "With AI, validation not code generation limits delivery", ["ch01", "ch03", "ch23", "ch25"], None),
 ]),
 ("Data platform", [
  ("Columnar segments & read-time aggregation", "Time-partitioned column files; prune; parallel scan; top-K", ["ch13", "ch14"], "06_columnar_store"),
  ("ClickHouse MergeTree", "Sorted immutable parts, sparse index, lazy materialisation", ["ch14"], None),
  ("Telemetry pipelines", "Collect, normalize, secure, enrich, reduce, route; agent+gateway", ["ch04", "ch16", "ch27"], "07_telemetry_pipeline"),
  ("Tiered telemetry & attribution", "Fidelity by criticality; cost per request/team", ["ch24", "ch27", "ch29"], "09_cost_and_ci"),
 ]),
 ("AI and new domains", [
  ("Agent context layer", "Topology, names, deploys, incidents, business context for agents", ["ch08", "ch10", "ch23"], None),
  ("AI sandwich & invariants", "Deterministic validation around nondeterministic proposals", ["ch17", "ch21"], "08_ai_sandwich"),
  ("LLM evals flywheel", "Traces → evals → harness fixes → telemetry", ["ch17", "ch21", "ch22"], "08_ai_sandwich"),
  ("Mobile: local buffer + control plane", "Log locally; server rules decide what to upload", ["ch19"], "10_mobile_ring_buffer"),
  ("User-focused SLIs", "Intention → outcome (checkout completion, TTFT, resolution)", ["ch19", "ch22"], "10_mobile_ring_buffer"),
 ]),
 ("Organisation & economics", [
  ("Sociotechnical debt", "Misaligned culture/process and technology", ["ch23", "ch24"], None),
  ("Observability as platform product", "Paved paths, devs as customers, report to engineering", ["ch04", "ch23", "ch26", "ch28", "ch29"], None),
  ("Business case & diagnosis", "Ops loop = cost center; dev loop = investment; leading indicators", ["ch26", "ch27"], None),
  ("Change management", "Five tests, coalition, mandate, one deep domain", ["ch28"], None),
  ("Build vs buy vs OSS", "2×2; price the puppy; buy platform, build glue", ["ch16", "ch29"], "09_cost_and_ci"),
 ]),
]

# Numbered requirements = an assessment checklist (source chapter, POC)
REQUIREMENTS = [
 ("R1", "Services you write emit one wide structured event (or root span) per unit of work with build, flags, route, user/tenant, key timings", "ch05, ch06", "01"),
 ("R2", "High-cardinality fields (user ID, build ID, trace ID) are queryable with no cardinality caps", "ch01, ch13", "06"),
 ("R3", "Any field can be grouped/filtered at read time in seconds; no pre-declared indexes needed", "ch03, ch13, ch28", "06"),
 ("R4", "Trace context propagates across HTTP, queues (links + correlation IDs) and async jobs", "ch05, ch07", "02"),
 ("R5", "Instrumentation uses OTel APIs; vendor specifics live in Collector/distro config", "ch04, ch07, ch29", "—"),
 ("R6", "Telemetry naming follows semantic conventions and a checked-in schema; fields have descriptions", "ch07, ch08, ch17, ch21", "—"),
 ("R7", "Every deploy is linked to its author with a cohort comparison (new vs old build) within minutes", "ch02, ch09, ch25, ch28", "03"),
 ("R8", "Deploys are decoupled from releases via feature flags; flag state is on every event", "ch02, ch06", "01"),
 ("R9", "Progressive delivery with automated rollback driven by precise signals", "ch02", "—"),
 ("R10", "Paging is driven by event-based SLO burn alerts with ≥2 lookahead windows; unactionable alerts are deleted", "ch11, ch12", "04"),
 ("R11", "Sampling records the rate on each event; errors/slow traces always kept; decisions consistent by trace ID", "ch15", "05"),
 ("R12", "A pipeline tier redacts PII centrally, enriches, reduces and routes; buffers with backoff and backpressure", "ch16, ch07", "07"),
 ("R13", "Telemetry fidelity is tiered by service criticality and adjustable without redeploys", "ch27, ch29", "07"),
 ("R14", "Observability cost is attributed per team/service and visible to them", "ch24, ch27, ch29", "09"),
 ("R15", "CI/CD workflows are traced; build time SLO and flake rate tracked", "ch18", "09"),
 ("R16", "Profiles are collected continuously and can be tied to spans or customers", "ch20", "—"),
 ("R17", "Mobile/frontend measure intention → outcome and can pull targeted sessions", "ch19", "10"),
 ("R18", "AI features log model, prompt version, tokens, feedback; bad traces promote to evals; AI outputs validated by invariants", "ch17, ch21", "08"),
 ("R19", "An agent-readable context layer exists: topology, aliases, owners, deploys, incidents, business criticality", "ch10", "—"),
 ("R20", "60–80% of engineers can investigate production independently; no 'two or three people' dependency", "ch01, ch28", "—"),
 ("R21", "Observability for product code reports to engineering and is run as a platform product", "ch23, ch26, ch28", "—"),
 ("R22", "Observability backend is operationally independent from production dependencies", "ch13, ch29", "—"),
]

# Interview drill bank: (question, crisp answer outline, chapters)
DRILLS = [
 ("Monitoring vs observability in one minute?", "Monitoring checks known failure conditions with pre-aggregated signals. Observability lets you ask new questions of raw, high-cardinality events at read time. You need both: monitoring for infrastructure, observability for your own code.", "ch01, ch03"),
 ("Why can't you just add user_id as a metric tag?", "Each unique tag combination becomes a new time series. Cost and query time blow up and vendors cap cardinality. Put it on events in a columnar store instead.", "ch01, ch13, ch24"),
 ("Explain how a trace is assembled.", "Each span has trace ID, span ID, parent ID, start and duration. Context propagates in-process (thread-local/async context) and across processes (W3C traceparent). The backend groups spans by trace ID and builds the tree from parent IDs.", "ch05, ch07"),
 ("Head vs tail sampling?", "Head decides at the root using only what's known at the start: cheap, consistent, but misses errors. Tail buffers the whole trace and decides on its outcome: needs a collector tier and memory, but keeps errors and slow traces.", "ch04, ch15"),
 ("How would you debug a latency spike in an unfamiliar service?", "Core analysis loop: confirm on a heatmap, select the slow band, diff dimensions against the baseline, take the strongest, filter, repeat, then look at an exemplar trace, then a profile.", "ch08"),
 ("Design an SLO for checkout.", "Eligible: POST /checkout root spans, excluding probes. Good: status < 400 and under 4 s. Target based on business cost and dependencies (e.g. 99.9%), sliding 30-day window, short and long burn alerts.", "ch11, ch12"),
 ("Why do canaries miss problems?", "Small error rates hide in noise, threshold and contention effects appear only at scale, aggregates smooth outliers, and samples aren't representative. Compare cohorts precisely and turn every escape into a health check.", "ch02"),
 ("Your observability bill doubled. What do you do?", "Diagnose before cutting: what do we use, what's never queried, which loop are we serving? Tier fidelity, sample by key, drop unqueried data in a pipeline, attribute cost per team, and check pricing models that penalise queries.", "ch16, ch24, ch27, ch29"),
 ("Build or buy observability?", "Usually buy the backend (commodity, must be independent of your own outages), build the glue (wrappers, naming, attribution) on OTel to avoid lock-in. Price self-hosting fully: engineers, hardware, upgrades, on-call.", "ch29"),
 ("How do you make an AI agent useful in incidents?", "Give it a context layer (topology, aliases, owners, recent deploys, incidents, business criticality), let it gather evidence and propose hypotheses, keep humans deciding, and measure time to understanding.", "ch08, ch10"),
 ("How do you observe an LLM feature?", "OTel GenAI spans (model, tokens, prompt version, tool calls), feedback attributes, cost derived from tokens, SLOs on provider calls, promote bad traces to evals, fix the harness before rewriting prompts.", "ch21"),
 ("How do you protect against AI hallucinations in a workflow that changes money?", "AI sandwich: the model emits a structured plan; a deterministic engine simulates it against invariants; reject mismatches; alert on the rejection rate; turn rejections into evals.", "ch17"),
 ("What's different about mobile observability?", "You don't control the environment, telemetry loss is biased toward bad sessions, workflows aren't auto-instrumentable, and bandwidth and battery matter. Use a local ring buffer, server-pushed rules, and intention → outcome SLIs by cohort.", "ch19"),
 ("How do you speed up a slow CI pipeline?", "Trace it, find the critical path, check whether each step is CPU, I/O or network bound by experiment, watch P50 vs P90 for retry tax, use caches, and remember Amdahl.", "ch18"),
 ("ClickHouse schema for traces: key decisions?", "Primary key matches the access path (ServiceName, Timestamp). Hot attributes as columns, the rest in Map/JSON. Bloom skip index on trace ID, materialized views for errors, TTL to S3, scale vertically before sharding.", "ch14"),
 ("How would you convince leadership to change observability approach?", "Run the five tests and collect evidence, frame it as risk, capability and burden (not cost or consolidation), find the executive who owns the pain, start with one deep domain, then rerun the tests.", "ch28, ch26"),
 ("What is sociotechnical debt?", "Accumulated misalignment between how people and process work and the technical system, e.g. developers never seeing production. AI amplifies it.", "ch23, ch24"),
 ("Why are event-based SLIs better than time-sliced?", "Each request counts proportionally. A minute with 6% slow requests burns 6%, not 100%. That gives more reaction time, better accuracy for brownouts, and you can backfill SLI changes.", "ch12"),
]
